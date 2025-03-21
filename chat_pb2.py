# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: chat.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'chat.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nchat.proto\x12\x04\x63hat\":\n\x16RegisterReplicaRequest\x12\x12\n\nip_address\x18\x01 \x01(\t\x12\x0c\n\x04port\x18\x02 \x01(\x05\"*\n\x17RegisterReplicaResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"9\n\x12MessageSyncRequest\x12#\n\x08messages\x18\x01 \x03(\x0b\x32\x11.chat.MessageData\"&\n\x13MessageSyncResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"0\n\x0fUserSyncRequest\x12\x1d\n\x05users\x18\x01 \x03(\x0b\x32\x0e.chat.UserData\"#\n\x10UserSyncResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\".\n\x16ReplicaListSyncRequest\x12\x14\n\x0creplica_list\x18\x01 \x03(\t\"*\n\x17ReplicaListSyncResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"%\n\x10HeartbeatRequest\x12\x11\n\tserver_id\x18\x01 \x01(\t\"$\n\x11HeartbeatResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"5\n\x12\x45lectLeaderRequest\x12\x11\n\tserver_id\x18\x01 \x01(\t\x12\x0c\n\x04term\x18\x02 \x01(\x03\"=\n\x13\x45lectLeaderResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x15\n\rnew_leader_id\x18\x02 \x01(\t\"(\n\x14LoginUsernameRequest\x12\x10\n\x08username\x18\x01 \x01(\t\">\n\x15LoginUsernameResponse\x12\x13\n\x0buser_exists\x18\x01 \x01(\x08\x12\x10\n\x08username\x18\x02 \x01(\t\":\n\x14LoginPasswordRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\"5\n\x15LoginPasswordResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0b\n\x03uid\x18\x02 \x01(\t\"\xa8\x01\n\x0bMessageData\x12\x0e\n\x06sender\x18\x01 \x01(\t\x12\x10\n\x08receiver\x18\x02 \x01(\t\x12\x17\n\x0fsender_username\x18\x03 \x01(\t\x12\x19\n\x11receiver_username\x18\x04 \x01(\t\x12\x0c\n\x04text\x18\x05 \x01(\t\x12\x0b\n\x03mid\x18\x06 \x01(\t\x12\x11\n\ttimestamp\x18\x07 \x01(\t\x12\x15\n\rreceiver_read\x18\x08 \x01(\x08\"}\n\x08UserData\x12\x0b\n\x03uid\x18\x01 \x01(\t\x12\x10\n\x08username\x18\x02 \x01(\t\x12\x10\n\x08password\x18\x03 \x01(\t\x12\x19\n\x11received_messages\x18\x04 \x03(\t\x12\x15\n\rsent_messages\x18\x05 \x03(\t\x12\x0e\n\x06\x61\x63tive\x18\x06 \x01(\x08\"#\n\x14\x44\x65leteAccountRequest\x12\x0b\n\x03uid\x18\x01 \x01(\t\"(\n\x15\x44\x65leteAccountResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"\'\n\x13ListAccountsRequest\x12\x10\n\x08wildcard\x18\x01 \x01(\t\"(\n\x14ListAccountsResponse\x12\x10\n\x08\x61\x63\x63ounts\x18\x01 \x03(\t\"`\n\x12SendMessageRequest\x12\x0e\n\x06sender\x18\x01 \x01(\t\x12\x19\n\x11receiver_username\x18\x02 \x01(\t\x12\x0c\n\x04text\x18\x03 \x01(\t\x12\x11\n\ttimestamp\x18\x04 \x01(\t\"&\n\x13SendMessageResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"!\n\x12GetMessagesRequest\x12\x0b\n\x03uid\x18\x01 \x01(\t\"#\n\x13GetMessagesResponse\x12\x0c\n\x04mids\x18\x01 \x03(\t\" \n\x11GetMessageRequest\x12\x0b\n\x03mid\x18\x01 \x01(\t\"\xaa\x01\n\x12GetMessageResponse\x12\x12\n\nsender_uid\x18\x01 \x01(\t\x12\x14\n\x0creceiver_uid\x18\x02 \x01(\t\x12\x17\n\x0fsender_username\x18\x03 \x01(\t\x12\x19\n\x11receiver_username\x18\x04 \x01(\t\x12\x0c\n\x04text\x18\x05 \x01(\t\x12\x11\n\ttimestamp\x18\x06 \x01(\t\x12\x15\n\rreceiver_read\x18\x07 \x01(\x08\"%\n\x16MarkMessageReadRequest\x12\x0b\n\x03mid\x18\x01 \x01(\t\"*\n\x17MarkMessageReadResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"2\n\x15\x44\x65leteMessagesRequest\x12\x0b\n\x03uid\x18\x01 \x01(\t\x12\x0c\n\x04mids\x18\x02 \x03(\t\")\n\x16\x44\x65leteMessagesResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x32\xae\t\n\x0b\x43hatService\x12H\n\rLoginUsername\x12\x1a.chat.LoginUsernameRequest\x1a\x1b.chat.LoginUsernameResponse\x12H\n\rLoginPassword\x12\x1a.chat.LoginPasswordRequest\x1a\x1b.chat.LoginPasswordResponse\x12H\n\rDeleteAccount\x12\x1a.chat.DeleteAccountRequest\x1a\x1b.chat.DeleteAccountResponse\x12\x45\n\x0cListAccounts\x12\x19.chat.ListAccountsRequest\x1a\x1a.chat.ListAccountsResponse\x12\x42\n\x0bSendMessage\x12\x18.chat.SendMessageRequest\x1a\x19.chat.SendMessageResponse\x12\x46\n\x0fGetSentMessages\x12\x18.chat.GetMessagesRequest\x1a\x19.chat.GetMessagesResponse\x12J\n\x13GetReceivedMessages\x12\x18.chat.GetMessagesRequest\x1a\x19.chat.GetMessagesResponse\x12\x44\n\x0fGetMessageByMid\x12\x17.chat.GetMessageRequest\x1a\x18.chat.GetMessageResponse\x12N\n\x0fMarkMessageRead\x12\x1c.chat.MarkMessageReadRequest\x1a\x1d.chat.MarkMessageReadResponse\x12K\n\x0e\x44\x65leteMessages\x12\x1b.chat.DeleteMessagesRequest\x1a\x1c.chat.DeleteMessagesResponse\x12N\n\x0fRegisterReplica\x12\x1c.chat.RegisterReplicaRequest\x1a\x1d.chat.RegisterReplicaResponse\x12M\n\x16SyncMessagesFromLeader\x12\x18.chat.MessageSyncRequest\x1a\x19.chat.MessageSyncResponse\x12\x44\n\x13SyncUsersFromLeader\x12\x15.chat.UserSyncRequest\x1a\x16.chat.UserSyncResponse\x12X\n\x19SyncReplicaListFromLeader\x12\x1c.chat.ReplicaListSyncRequest\x1a\x1d.chat.ReplicaListSyncResponse\x12<\n\tHeartbeat\x12\x16.chat.HeartbeatRequest\x1a\x17.chat.HeartbeatResponse\x12\x42\n\x0b\x45lectLeader\x12\x18.chat.ElectLeaderRequest\x1a\x19.chat.ElectLeaderResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chat_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_REGISTERREPLICAREQUEST']._serialized_start=20
  _globals['_REGISTERREPLICAREQUEST']._serialized_end=78
  _globals['_REGISTERREPLICARESPONSE']._serialized_start=80
  _globals['_REGISTERREPLICARESPONSE']._serialized_end=122
  _globals['_MESSAGESYNCREQUEST']._serialized_start=124
  _globals['_MESSAGESYNCREQUEST']._serialized_end=181
  _globals['_MESSAGESYNCRESPONSE']._serialized_start=183
  _globals['_MESSAGESYNCRESPONSE']._serialized_end=221
  _globals['_USERSYNCREQUEST']._serialized_start=223
  _globals['_USERSYNCREQUEST']._serialized_end=271
  _globals['_USERSYNCRESPONSE']._serialized_start=273
  _globals['_USERSYNCRESPONSE']._serialized_end=308
  _globals['_REPLICALISTSYNCREQUEST']._serialized_start=310
  _globals['_REPLICALISTSYNCREQUEST']._serialized_end=356
  _globals['_REPLICALISTSYNCRESPONSE']._serialized_start=358
  _globals['_REPLICALISTSYNCRESPONSE']._serialized_end=400
  _globals['_HEARTBEATREQUEST']._serialized_start=402
  _globals['_HEARTBEATREQUEST']._serialized_end=439
  _globals['_HEARTBEATRESPONSE']._serialized_start=441
  _globals['_HEARTBEATRESPONSE']._serialized_end=477
  _globals['_ELECTLEADERREQUEST']._serialized_start=479
  _globals['_ELECTLEADERREQUEST']._serialized_end=532
  _globals['_ELECTLEADERRESPONSE']._serialized_start=534
  _globals['_ELECTLEADERRESPONSE']._serialized_end=595
  _globals['_LOGINUSERNAMEREQUEST']._serialized_start=597
  _globals['_LOGINUSERNAMEREQUEST']._serialized_end=637
  _globals['_LOGINUSERNAMERESPONSE']._serialized_start=639
  _globals['_LOGINUSERNAMERESPONSE']._serialized_end=701
  _globals['_LOGINPASSWORDREQUEST']._serialized_start=703
  _globals['_LOGINPASSWORDREQUEST']._serialized_end=761
  _globals['_LOGINPASSWORDRESPONSE']._serialized_start=763
  _globals['_LOGINPASSWORDRESPONSE']._serialized_end=816
  _globals['_MESSAGEDATA']._serialized_start=819
  _globals['_MESSAGEDATA']._serialized_end=987
  _globals['_USERDATA']._serialized_start=989
  _globals['_USERDATA']._serialized_end=1114
  _globals['_DELETEACCOUNTREQUEST']._serialized_start=1116
  _globals['_DELETEACCOUNTREQUEST']._serialized_end=1151
  _globals['_DELETEACCOUNTRESPONSE']._serialized_start=1153
  _globals['_DELETEACCOUNTRESPONSE']._serialized_end=1193
  _globals['_LISTACCOUNTSREQUEST']._serialized_start=1195
  _globals['_LISTACCOUNTSREQUEST']._serialized_end=1234
  _globals['_LISTACCOUNTSRESPONSE']._serialized_start=1236
  _globals['_LISTACCOUNTSRESPONSE']._serialized_end=1276
  _globals['_SENDMESSAGEREQUEST']._serialized_start=1278
  _globals['_SENDMESSAGEREQUEST']._serialized_end=1374
  _globals['_SENDMESSAGERESPONSE']._serialized_start=1376
  _globals['_SENDMESSAGERESPONSE']._serialized_end=1414
  _globals['_GETMESSAGESREQUEST']._serialized_start=1416
  _globals['_GETMESSAGESREQUEST']._serialized_end=1449
  _globals['_GETMESSAGESRESPONSE']._serialized_start=1451
  _globals['_GETMESSAGESRESPONSE']._serialized_end=1486
  _globals['_GETMESSAGEREQUEST']._serialized_start=1488
  _globals['_GETMESSAGEREQUEST']._serialized_end=1520
  _globals['_GETMESSAGERESPONSE']._serialized_start=1523
  _globals['_GETMESSAGERESPONSE']._serialized_end=1693
  _globals['_MARKMESSAGEREADREQUEST']._serialized_start=1695
  _globals['_MARKMESSAGEREADREQUEST']._serialized_end=1732
  _globals['_MARKMESSAGEREADRESPONSE']._serialized_start=1734
  _globals['_MARKMESSAGEREADRESPONSE']._serialized_end=1776
  _globals['_DELETEMESSAGESREQUEST']._serialized_start=1778
  _globals['_DELETEMESSAGESREQUEST']._serialized_end=1828
  _globals['_DELETEMESSAGESRESPONSE']._serialized_start=1830
  _globals['_DELETEMESSAGESRESPONSE']._serialized_end=1871
  _globals['_CHATSERVICE']._serialized_start=1874
  _globals['_CHATSERVICE']._serialized_end=3072
# @@protoc_insertion_point(module_scope)
