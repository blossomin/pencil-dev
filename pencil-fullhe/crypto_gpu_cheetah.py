# import tools.pytroy as pytroy
import pytroy
import numpy as np
import math
import time
# from utils import GeneralVectorDataType, GeneralEncoder, GeneralVector, GeneralHeContext

# Note: if you would use the product of secret shares (say, attention)
# you would need 8192, (60, 60, 60) and precision 25 bits
# If you only need secret shares * value completedly owned by one party
# you can use 4096, (60, 49) and precision 12 bits.
# When you change this, remember to change the import sci_provider
# in communication_*.py to the corresponding bit length.

BFV_POLY_DEGREE = 8192
BFV_Q_BITS = (60, 60, 60)
PLAIN_MODULUS = 1 << 59
SCALE_BITS = 25
SCALE = 1<<SCALE_BITS
MOD_SWITCH_TO_NEXT = len(BFV_Q_BITS) > 2

# USE_DEVICE = True

def initialize_kernel():
  pytroy.initialize_kernel(0)

def get2e(p):
  i=1
  while i<p: i*=2
  return i


class EvaluationUtils:

  def __init__(self):
    self.slot_count = BFV_POLY_DEGREE
    pass

  def receive_keys(self, params_set):
    self.bfv_params = pytroy.EncryptionParameters(pytroy.SchemeType.BFV)
    self.bfv_params.set_poly_modulus_degree(BFV_POLY_DEGREE)
    self.bfv_params.set_plain_modulus(PLAIN_MODULUS)
    # print(f"CKKS max bit count = {seal.CoeffModulus.MaxBitCount(POLY_MODULUS_DEGREE)}")
    self.bfv_params.set_coeff_modulus(pytroy.CoeffModulus.create(BFV_POLY_DEGREE, BFV_Q_BITS))
    self.bfv_context = pytroy.HeContext(self.bfv_params)
    s_public_key, s_relin_key = params_set
    self.public_key = pytroy.PublicKey()
    self.public_key.load(s_public_key, self.bfv_context)
    self.relin_key = pytroy.RelinKeys()
    self.relin_key.load(s_relin_key, self.bfv_context)
    self.bfv_context = pytroy.HeContext(self.bfv_params)
    self.encryptor = pytroy.Encryptor(self.bfv_context)
    self.evaluator = pytroy.Evaluator(self.bfv_context)
    self.encoder = pytroy.BatchEncoder(self.bfv_context)
    self.slot_count = self.encoder.slot_count()
    self.keygen = pytroy.KeyGenerator(self.bfv_context)
    self.automorphism_keys = self.keygen.create_automorphism_keys(False)

    # if USE_DEVICE:
    #     self.bfv_context.to_device_inplace()
    #     self.encryptor.to_device_inplace()
    #     self.encoder.to_device_inplace()
    #     self.keygen.to_device_inplace()

  def to_field(self, a: np.ndarray, scale=SCALE, flatten=True):
    if flatten: a = a.flatten()
    a = a * scale
    a = np.where(a < 0, PLAIN_MODULUS + a, a).astype(np.uint64)
    return a

  def field_random_mask(self, size):
    return np.random.randint(0, PLAIN_MODULUS, size, dtype=np.uint64)

  def field_negate(self, x):
    return np.mod(PLAIN_MODULUS - x, PLAIN_MODULUS)

  def field_mod(self, x):
    return np.mod(x, PLAIN_MODULUS)

  def field_add(self, x, y):
    return np.mod(x + y, PLAIN_MODULUS)

  def to_decimal(self, a: np.ndarray, scale=SCALE, shape=None):
    a = a.astype(np.float64)
    a = np.where(a > PLAIN_MODULUS // 2, a - PLAIN_MODULUS, a) / scale
    if shape is not None:
      a = np.reshape(a, shape)
    return a

  def default_scale(self): return SCALE

  def serialize(self, c):
    return c.save(self.bfv_context, pytroy.CompressionMode.Nil)

  def deserialize(self, c):
    ret = pytroy.Cipher2d()
    ret.load(c, self.bfv_context)
    return ret




  def matmul_helper(self, batchsize, input_dims, output_dims, objective):
    # print("MatmulHelper: ", batchsize, input_dims, output_dims, objective)
    ret = None
    if objective == 0:
        objective_params = pytroy.MatmulObjective.EncryptLeft
    elif objective == 1:
        objective_params = pytroy.MatmulObjective.EncryptRight
    elif objective == 2:
        objective_params = pytroy.MatmulObjective.Crossed
    else:
        raise Exception("Invalid objective")
    try:
        ret = pytroy.MatmulHelper(batchsize, input_dims, output_dims, self.slot_count, objective_params, True)
    except Exception as e:
        print(e)
        raise e
    # print("Helper ok")
    return ret

  def matmul_encode_x(self, helper, x):
    return helper.encode_inputs(self.encoder, x)

  def matmul_encode_y(self, helper, y):
    return helper.encode_outputs(self.encoder, y)

  def matmul_encode_w(self, helper, w):
    w = w.flatten()
    return helper.encode_weights(self.encoder, w)

  def matmul(self, helper, x, w):
    ret = helper.matmul(self.evaluator, x, w)
    if MOD_SWITCH_TO_NEXT: ret.mod_switch_to_next(self.evaluator)
    return ret
  def matmul_reverse(self, helper, x, w):
    ret = helper.matmul_reverse(self.evaluator, x, w)
    if MOD_SWITCH_TO_NEXT: ret.mod_switch_to_next(self.evaluator)
    return ret
  def matmul_serialize_y(self, helper, y):
    return helper.serialize_outputs(self.evaluator, y)

  def matmul_deserialize_y(self, helper, s):
    return helper.deserialize_outputs(self.evaluator, s)

  def matmul_pack_outputs(self, helper, y):
    return helper.pack_outputs(self.evaluator, self.automorphism_keys, y)


  def conv2d_helper(self, batchsize, image_height, image_width, kernel_height, kernel_width, input_channels, output_channels, objective):
    # print("Conv2dHelper: ", batchsize, batchsize, image_height, image_width, kernel_height, kernel_width, input_channels, output_channels)
    ret = None
    if objective == 0:
        objective_params = pytroy.MatmulObjective.EncryptLeft
    elif objective == 1:
        objective_params = pytroy.MatmulObjective.EncryptRight
    elif objective == 2:
        objective_params = pytroy.MatmulObjective.Crossed
    else:
        raise Exception("Invalid objective")
    try:
        ret = pytroy.Conv2dHelper(
        batchsize, input_channels, output_channels, image_height, image_width, kernel_height, kernel_width,
        self.slot_count, objective_params)
    except Exception as e:
        print(e)
        raise e
    # print("Helper ok")
    return ret

  def conv2d_encode_x(self, helper, x):
    return helper.encode_inputs(self.encoder, x)

  def conv2d_encode_y(self, helper, y):
    return helper.encode_outputs(self.encoder, y)

  def conv2d_encode_w(self, helper, w):
    return helper.encode_weights(self.encoder, w)

  def conv2d(self, helper, x, w):
    ret = helper.conv2d(self.evaluator, x, w)
    if MOD_SWITCH_TO_NEXT: ret.mod_switch_to_next(self.evaluator)
    return ret

  def conv2d_reverse(self, helper, x, w):
    ret = helper.conv2d_reverse(self.evaluator, x, w)
    if MOD_SWITCH_TO_NEXT: ret.mod_switch_to_next(self.evaluator)
    return ret

  def conv2d_serialize_y(self, helper, y):
    return helper.serialize_outputs(self.evaluator, y)

  def conv2d_deserialize_y(self, helper, s):
    return helper.deserialize_outputs(self.evaluator, s)

  def encrypt_cipher2d(self, x):
    # print(f"encrypt_cipher2d: {x.size(), x.rows(), x.columns()}")
    return x.encrypt_symmetric(self.encryptor)

  def add_plain_inplace(self, x, y):
    # print(f"add_plain_inplace: {x.size(), x.rows(), x.columns()}")
    x.add_plain_inplace(self.evaluator, y)

  def add_inplace(self, x, y):
    # print(f"add_inplace: {x.size(), x.rows(), x.columns()}")
    x.add_inplace(self.evaluator, y)

  def add_plain(self, x, y):
    # print(f"add_plain: {x.size(), x.rows(), x.columns()}")
    return x.add_plain(y)

  
  def relu_plain(self, x):
    return np.where(x > PLAIN_MODULUS//2, 0, x)

  def drelumul_plain(self, x, y):
    return np.where(x > PLAIN_MODULUS//2, 0, y)

  def truncate_plain(self, x, scale:int=SCALE):
    return np.where(x > PLAIN_MODULUS//2, PLAIN_MODULUS - (PLAIN_MODULUS - x) // scale, x // scale)

  def divide_plain(self, x, divident):
    return np.where(x > PLAIN_MODULUS//2, PLAIN_MODULUS - (PLAIN_MODULUS - x) // divident, x // divident)



class EncryptionUtils(EvaluationUtils):

  def __init__(self):
    super().__init__()

  def generate_keys(self):
    self.bfv_params = pytroy.EncryptionParameters(pytroy.SchemeType.BFV)
    self.bfv_params.set_poly_modulus_degree(BFV_POLY_DEGREE)
    self.bfv_params.set_plain_modulus(PLAIN_MODULUS)
    # print(f"CKKS max bit count = {pytroy.CoeffModulus.MaxBitCount(POLY_MODULUS_DEGREE)}")
    self.bfv_params.set_coeff_modulus(pytroy.CoeffModulus.create(BFV_POLY_DEGREE, BFV_Q_BITS))
    self.bfv_context = pytroy.HeContext(self.bfv_params)
    # self.bfv_context.to_device_inplace()
    self.keygen = pytroy.KeyGenerator(self.bfv_context)
    self.secret_key = self.keygen.secret_key()
    self.public_key = self.keygen.create_public_key(False)
    self.relin_key = self.keygen.create_relin_keys(False)
    self.encryptor = pytroy.Encryptor(self.bfv_context)
    self.decryptor = pytroy.Decryptor(self.bfv_context, self.secret_key)
    self.evaluator = pytroy.Evaluator(self.bfv_context)
    self.encoder = pytroy.BatchEncoder(self.bfv_context)
    self.slot_count = self.encoder.slot_count()

    self.encryptor.set_secret_key(self.keygen.secret_key())

    # x1 = self.encoder.encode_polynomial(np.array([1,2,3,4], dtype=np.uint64))
    # y1 = self.encryptor.encrypt(x1)
    # x2 = self.encoder.encode_polynomial(np.array([1,2,3,4], dtype=np.uint64))
    # y2 = self.encryptor.encrypt(x2)
    # if USE_DEVICE:
    #     self.bfv_context.to_device_inplace()
    #     self.encryptor.to_device_inplace()
    #     self.decryptor.to_device_inplace()
    #     self.encoder.to_device_inplace()
    #     self.keygen.to_device_inplace()

    return (self.public_key.save(self.bfv_context), self.relin_key.save(self.bfv_context))
      
  def matmul_decrypt_y(self, helper, y):
    return helper.decrypt_outputs(self.encoder, self.decryptor, y)

  def conv2d_decrypt_y(self, helper, y):
    return helper.decrypt_outputs(self.encoder, self.decryptor, y)

