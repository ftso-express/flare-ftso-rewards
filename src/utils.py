from web3 import Web3

def get_ftso_manager_address_from_price_submitter(web3: Web3, contract_price_submitter):
  return contract_price_submitter.functions.getFtsoManager().call()




# def get_methods(object, spacing=20):
#   methodList = []
#   for method_name in dir(object):
#     try:
#         if callable(getattr(object, method_name)):
#             methodList.append(str(method_name))
#     except Exception:
#         methodList.append(str(method_name))
#   processFunc = (lambda s: ' '.join(s.split())) or (lambda s: s)
#   for method in methodList:
#     try:
#         print(str(method.ljust(spacing)) + ' ' +
#               processFunc(str(getattr(object, method).__doc__)[0:90]))
#     except Exception:
#         print(method.ljust(spacing) + ' ' + ' getattr() failed')