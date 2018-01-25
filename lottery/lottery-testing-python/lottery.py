#!/usr/bin/python3 -i
from web3 import Web3, HTTPProvider
import sys
import json
import time

web3 = Web3(HTTPProvider('http://localhost:7999'))

eth = web3.eth

contract_name = "LotteryInvestment"

with open("build/" + contract_name + ".abi") as contract_abi_file:
  contract_abi = json.load(contract_abi_file)

#Comes as string without '0x'
contract_bin = open("build/" + contract_name + ".bin").read()
contract = eth.contract(contract_abi, bytecode=("0x" + contract_bin))

def trans(from_index=0, value=0):
  return {"from": eth.accounts[from_index], "value": value*(10**18), "gas": 7000000, "gasPrice": 0}

#params = [ [eth.accounts[1], eth.accounts[2], eth.accounts[3]], [40000, 30000, 30000] ]

dHash = contract.deploy(transaction=trans(0,0))

#name_and_gas = lambda tx_hash : print(sys._getframe().f_code.co_name + ":", gas(tx_hash))

def receipt(tx_hash):
  return eth.getTransactionReceipt(tx_hash)

def status(tx_hash):
  print("Status:", eth.getTransactionReceipt(tx_hash)["status"])

def gas(tx_hash):
  return eth.getTransactionReceipt(tx_hash)["gasUsed"]

def addAddress():
  time.sleep(2)
  status(dHash)
  gas(dHash)
  contract.address = receipt(dHash).contractAddress
  print(contract_name, contract.address)

def balance(address_or_index):
  if isinstance(address_or_index, str):
    return web3.fromWei(eth.getBalance(address_or_index), "ether")
    #return eth.getBalance(address_or_index)
  else:
    return web3.fromWei(eth.getBalance(eth.accounts[address_or_index]), "ether")
    #return eth.getBalance(eth.accounts[address_or_index])

def balances():
  bals = []
  for acc in eth.accounts:
    bals.append(balance(acc))
  return bals

def buy(buyer_index, value):
  tx_hash = eth.sendTransaction({"from": eth.accounts[buyer_index], "value": value*(10**18), "gas": 200000, "gasPrice": 0, "to": contract.address})
  time.sleep(2)
  print(sys._getframe().f_code.co_name, gas(tx_hash))
  
def partners():
  partners = []
  partners.append(contract.call().investment_address())
  partners.append(contract.call().major_partner_address())
  partners.append(contract.call().minor_partner_address())
  return partners

def partners_balances():
  bals = []
  parts = partners()
  for part in parts:
    bals.append(balance(part))
  return bals

def set_transfer_gas(gas_amount):
  tx_hash = contract.transact(trans()).set_transfer_gas(gas_amount)
  time.sleep(2)
  print(sys._getframe().f_code.co_name, gas(tx_hash))

def lifecycle():
  init_bals = balances()
  contract_bal_i = balance(contract.address)
  partners_bals_i = partners_balances()
  buy(1,1000)  
  buy(2,1000)
  buy(3,2000)
  last_bals = balances()
  contract_bal_f = balance(contract.address)
  partners_bals_f = partners_balances()
  print("Investors balances differences:", [x-y for x, y in zip(init_bals,last_bals)])  
  print("Contract balance difference:", contract_bal_i - contract_bal_f)
  print("Partners balances differences", [x-y for x, y in zip(partners_bals_i, partners_bals_f)])

addAddress()

