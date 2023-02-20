from web3 import Web3
import numpy as np

from base_logger import log

log.propagate = False

def get_songbird_wallet_balances_sgb(web3: Web3, _wallet_account):
        sgb_wallet_amount = web3.eth.get_balance(_wallet_account,)
        # wsgb_wallet_amount = web3.eth.contract(address=contracts["WrappedFlare"]["address"], abi=contracts["WrappedFlare"]["abi"])

def get_songbird_wallet_balances_wsgb(web3: Web3, _wallet_account, _contract_wnat, _CONTRACT_WNAT):
        wsgb_amount = web3.eth.contract(address=_CONTRACT_WNAT["address"], abi=_CONTRACT_WNAT["abi"])
        log.debug(f"WSGB Amounts: {wsgb_amount}")
        return wsgb_amount

def get_songbird_current_reward_epoch(web3: Web3, _contract_ftso_reward_manager) -> int:
    _current_songbird_reward_epoch = _contract_ftso_reward_manager.functions.getCurrentRewardEpoch().call()
    log.info(f"Current Reward Epoch: {_current_songbird_reward_epoch}")
    return _current_songbird_reward_epoch

def get_songbird_claimable_reward_epoch_range(web3: Web3, _contract_ftso_reward_manager) -> (int,int):
    # Call - getEpochsWithClaimableRewards
    _songbird_claimable_reward_epoch_min, _songbird_claimable_reward_epoch_max = _contract_ftso_reward_manager.functions.getEpochsWithClaimableRewards().call()
    log.info(f"Current Claimable Reward Epoch Range: {_songbird_claimable_reward_epoch_min} - {_songbird_claimable_reward_epoch_max}")
    return (_songbird_claimable_reward_epoch_min, _songbird_claimable_reward_epoch_max)
    
def get_songbird_pricing_epoch_for_rewards_unclaimed(web3: Web3, _ftso_account, _contract_ftso_reward_manager):
    _unclaimed_ftso_reward_epochs = _contract_ftso_reward_manager.functions.getEpochsWithUnclaimedRewards(_ftso_account.address).call()
    log.info(f"FTSO Unclaimed Rewards Balance: {_ftso_account.address} {_unclaimed_ftso_reward_epochs}")
    return _unclaimed_ftso_reward_epochs

def get_songbird_rewards_claimable_from_ftso_rewards_manager(web3: Web3, _ftso_account, _contract_ftso_reward_manager, _CONTRACT_FTSO_REWARD_MANAGER, _ftso_rewards_epochs_claimable):
    contract_ftso_reward_manager_balance = web3.fromWei(web3.eth.get_balance(_CONTRACT_FTSO_REWARD_MANAGER['address']),'ether')
    log.debug(f"FTSO Rewards Balance: {contract_ftso_reward_manager_balance}")
    _unclaimed_rewards_epoch_list = []
    for x in _ftso_rewards_epochs_claimable:
        _amount, _weight = _contract_ftso_reward_manager.functions.getUnclaimedReward(x,_ftso_account.address).call()
        # _unclaimed_rewards_epoch_list[f"unclaimed_epoch_{x}"] = {
        #     'amount_wei': _amount,
        #     'amount_sgb': web3.fromWei(_amount, 'ether'),
        #     'weight_wei': _weight,
        #     'weight_sgb': web3.fromWei(_weight, 'ether'),
        # }
        _ = {
            'epoch'     : x,
            'amount_wei': _amount,
            'amount_sgb': web3.fromWei(_amount, 'ether'),
            'weight_wei': _weight,
            'weight_sgb': web3.fromWei(_weight, 'ether'),
        }
        _unclaimed_rewards_epoch_list.append(_)

    log.debug(f"FTSO Rewards Unclaimed Per Epoch: {_unclaimed_rewards_epoch_list}[{len(_unclaimed_rewards_epoch_list)}]")

    return _unclaimed_rewards_epoch_list

def get_state_of_rewards_songbird(web3: Web3, _ftso_account, _contract_ftso_reward_manager, _current_songbird_reward_epoch, _claim_epoch_range_min):
    state_of_rewards_list = {}
    for x in range(_claim_epoch_range_min,_current_songbird_reward_epoch):
        _dataProviders, _rewardAmounts, _claimed, _claimable = _contract_ftso_reward_manager.functions.getStateOfRewards(_ftso_account.address,x).call()
        state_of_rewards_list[f"epoch{x}"] = {
            # 'Data_Providers': _dataProviders,
            'Reward_Amounts_[WEI]': _rewardAmounts[0] if _rewardAmounts else np.NaN,
            'Reward_Amounts_[FLR]': web3.fromWei(_rewardAmounts[0] if _rewardAmounts else np.NaN,  'ether'),
            'Claimed': _claimed,
            'Claimable': _claimable,
        }
    return state_of_rewards_list

def execute_reward_claim_songbird(web3: Web3, _ftso_account, _FTSO_PRIVATE_KEY, _contract_ftso_reward_manager, _wallet_to_reward, _ftso_rewards_epochs_to_claim, _GAS_LIMIT, _GAS_PRICE):
    log.warning(f"FTOS Private Key: {_ftso_account}")
    # Get Nonce
    try:
        nonce = web3.eth.getTransactionCount(_ftso_account.address)
        log.debug(f"nonce: {nonce}")
    except Exception as error:
        log.warning(f"Web3 (getTransactionCount) Error - getTransactionCount - {error}")
        raise Exception(f"Boom, it's broke - {error}")

    # Create TXN
    try:
        submission_txn = _contract_ftso_reward_manager.functions.claimReward(
                                _wallet_to_reward,
                                [_ftso_rewards_epochs_to_claim] 
                            ).buildTransaction(
                                {
                                    'nonce': nonce,
                                    'gas': _GAS_LIMIT,
                                    'gasPrice': web3.toWei(_GAS_PRICE, 'gwei'),
                                }
                            )
        log.debug(f"submission_txn: {submission_txn}")
    except Exception as error:
        log.warning(f"Web3 (submission_txn) Error - ContractLogicError {error} ")
        raise Exception(f"Boom, it's broke - {error}")

    # Sign TXN
    try:
        signed_txn = web3.eth.account.signTransaction(submission_txn, _FTSO_PRIVATE_KEY)
        log.debug(f"signed_txn: {signed_txn}")
    except Exception as error:
        log.warning(f"Web3 (signed_txn) Error - General Transaction - {error}")
        raise Exception(f"Boom, it's broke - {error}")

    # Send TXN
    try:
        txid = web3.toHex(web3.eth.sendRawTransaction(signed_txn.rawTransaction))
        log.debug(f"txid: {txid}")
    # except exceptions.ContractLogicError as error:
    #     log.warning(
    #         "Web3 (submitPriceHashes) Error - ContractLogicError",
    #         type="submission",
    #         exception="web3.ContractLogicError",
    #         error=error,
    #         # info=str(submission_string)
    #     )
    #     # exit()
    # except exceptions.ValidationError as error:
    #     log.warning(
    #         "Web3 (submitPriceHashes) Error - ValidationError",
    #         exception="web3.ValidationError",
    #         error=error,
    #         # info=str(submission_string)
    #     )
    #     # exit()
    # except ValueError as error:
    #     log.warning(
    #         "Web3 (submitPriceHashes) Error - ValueError",
    #         exception="ValueError",
    #         error=error,
    #         # info=str(submission_string)
    #     )
    #     # exit()
    # except TypeError as error:
    #     log.warning(
    #         "Web3 (submitPriceHashes) Error - TypeError",
    #         exception="TypeError",
    #         error=error,
    #         # info=str(submission_string)
    #     )
    #     # exit()
    # except UnboundLocalError as error:
    #     log.warning(
    #         "Web3 (submitPriceHashes) Error - UnboundLocalError",
    #         exception="UnboundLocalError",
    #         error=error,
    #         # info=str(submission_string)
    #     )
    #     # exit()
    except Exception as error:
        log.warning(f"Web3 (txid) Error - General Exception {error}")
        raise Exception(f"Boom, it's broke - {error}")
        # WARNING  Web3 (txid) Error - General Exception {'code': -32000, 'message': 'replacement transaction underpriced'}  

    # Wait for Receipt
    try:
        tx_receipt = web3.eth.waitForTransactionReceipt(txid,timeout=240)
        log.debug(f"waitForTransactionReceipt - TX RCPT{tx_receipt}")
    except Exception as error:
        log.warning(f"Web3 (tx_receipt) Error - Wait For Transaction")
        raise Exception(f"Boom, it's broke - {error}")

    return tx_receipt