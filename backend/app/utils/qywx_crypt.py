#!/usr/bin/env python
# -*- encoding:utf-8 -*-

""" 企业微信回调消息加解密工具
"""

import base64
import string
import random
import hashlib
import time
import struct
from Crypto.Cipher import AES
import xml.etree.cElementTree as ET
import socket
import logging

logger = logging.getLogger(__name__)

class SHA1:
    """计算企业微信的消息签名接口"""
    
    @staticmethod
    def getSHA1(token, timestamp, nonce, encrypt):
        """用SHA1算法生成安全签名
        @param token:  票据
        @param timestamp: 时间戳
        @param nonce: 随机字符串
        @param encrypt: 密文
        @return: 安全签名
        """
        try:
            sortlist = [token, timestamp, nonce, encrypt]
            sortlist.sort()
            sha = hashlib.sha1()
            sha.update("".join(sortlist).encode())
            return sha.hexdigest()
        except Exception as e:
            logger.exception(f"计算SHA1签名失败: {e}")
            return ""


class PKCS7Encoder():
    """提供基于PKCS7算法的加解密接口"""

    block_size = 32
    
    def encode(self, text):
        """ 对需要加密的明文进行填充补位
        @param text: 需要进行填充补位操作的明文
        @return: 补齐明文字符串
        """
        text_length = len(text)
        # 计算需要填充的位数
        amount_to_pad = self.block_size - (text_length % self.block_size)
        if amount_to_pad == 0:
            amount_to_pad = self.block_size
        # 获得补位所用的字符
        pad = chr(amount_to_pad)
        return text + (pad * amount_to_pad).encode()
    
    def decode(self, decrypted):
        """删除解密后明文的补位字符
        @param decrypted: 解密后的明文
        @return: 删除补位字符后的明文
        """
        pad = decrypted[-1]
        if pad < 1 or pad > 32:
            pad = 0
        return decrypted[:-pad]


class Prpcrypt(object):
    """提供接收和推送给企业微信消息的加解密接口"""

    def __init__(self, key):
        self.key = key
        # 设置加解密模式为AES的CBC模式
        self.mode = AES.MODE_CBC

    def encrypt(self, text, receiveid):
        """对明文进行加密
        @param text: 需要加密的明文
        @param receiveid: 企业微信的CorpID/ReceiveID
        @return: 加密得到的字符串
        """
        try:
            # 16位随机字符串添加到明文开头
            text = text.encode()
            text = self.get_random_str() + struct.pack("!I", len(text)) + text + receiveid.encode()
            
            # 使用自定义的填充方式对明文进行补位填充
            pkcs7 = PKCS7Encoder()
            text = pkcs7.encode(text)
            
            # 加密
            cryptor = AES.new(self.key, self.mode, self.key[:16])
            try:
                ciphertext = cryptor.encrypt(text)
                # 使用BASE64对加密后的字符串进行编码
                return base64.b64encode(ciphertext)
            except Exception as e:
                logger.exception(f"加密失败: {e}")
                return None
        except Exception as e:
            logger.exception(f"加密失败: {e}")
            return None

    def decrypt(self, text, receiveid):
        """对解密后的明文进行补位删除
        @param text: 密文
        @param receiveid: 企业微信的CorpID/ReceiveID
        @return: 删除填充补位后的明文
        """
        try:
            cryptor = AES.new(self.key, self.mode, self.key[:16])
            # 使用BASE64对密文进行解码，然后AES-CBC解密
            plain_text = cryptor.decrypt(base64.b64decode(text))
            
            # 去掉补位字符
            pkcs7 = PKCS7Encoder()
            plain_text = pkcs7.decode(plain_text)
            
            # 去除16位随机字符串
            content = plain_text[16:]
            xml_len = socket.ntohl(struct.unpack("!I", content[:4])[0])
            xml_content = content[4:xml_len+4]
            from_receiveid = content[xml_len+4:].decode()
            
            if from_receiveid != receiveid:
                logger.error(f"receiveid不匹配: {from_receiveid} != {receiveid}")
                return None
            return xml_content
        except Exception as e:
            logger.exception(f"解密失败: {e}")
            return None

    def get_random_str(self):
        """ 随机生成16位字符串
        @return: 16位字符串
        """
        rule = string.ascii_letters + string.digits
        str = random.sample(rule, 16)
        return "".join(str).encode()


class WXBizMsgCrypt(object):
    """企业微信消息加解密类"""
    
    def __init__(self, token, encodingAESKey, receiveid):
        """初始化
        @param token: 企业微信后台提供的接收消息Token
        @param encodingAESKey: 企业微信后台提供的接收消息EncodingAESKey
        @param receiveid: 企业号的CorpID或第三方应用的SuiteID
        """
        try:
            self.token = token
            self.receiveid = receiveid
            self.AES_KEY = base64.b64decode(encodingAESKey + "=")
            self.pc = Prpcrypt(self.AES_KEY)
        except Exception as e:
            logger.exception(f"初始化失败: {e}")

    def VerifyURL(self, sMsgSignature, sTimeStamp, sNonce, sEchoStr):
        """验证回调URL有效性
        @param sMsgSignature: 签名串，对应URL参数的msg_signature
        @param sTimeStamp: 时间戳，对应URL参数的timestamp
        @param sNonce: 随机串，对应URL参数的nonce
        @param sEchoStr: 随机串，对应URL参数的echostr
        @return: 解密之后的echostr，当return返回0时有效
        """
        signature = SHA1.getSHA1(self.token, sTimeStamp, sNonce, sEchoStr)
        if signature != sMsgSignature:
            logger.error(f"签名验证失败: {signature} != {sMsgSignature}")
            return -1, "签名验证失败"
        
        result = self.pc.decrypt(sEchoStr, self.receiveid)
        if not result:
            return -1, "解密失败"
        
        return 0, result.decode()

    def DecryptMsg(self, sPostData, sMsgSignature, sTimeStamp, sNonce):
        """检验消息的真实性，并且获取解密后的明文
        @param sPostData: 密文，对应POST请求的数据
        @param sMsgSignature: 签名串，对应URL参数的msg_signature
        @param sTimeStamp: 时间戳，对应URL参数的timestamp
        @param sNonce: 随机串，对应URL参数的nonce
        @return: 解密后的原文
        """
        # 解析xml,获取Encrypt标签数据
        try:
            xml_tree = ET.fromstring(sPostData)
            encrypt = xml_tree.find("Encrypt")
            if encrypt is None:
                return -1, "无法找到Encrypt标签"
            
            # 验证安全签名
            signature = SHA1.getSHA1(self.token, sTimeStamp, sNonce, encrypt.text)
            if signature != sMsgSignature:
                logger.error(f"签名验证失败: {signature} != {sMsgSignature}")
                return -1, "签名验证失败"
            
            # 解密
            result = self.pc.decrypt(encrypt.text, self.receiveid)
            if not result:
                return -1, "解密失败"
            
            return 0, result.decode()
        except Exception as e:
            logger.exception(f"解密消息失败: {e}")
            return -1, "解密消息失败"

    def EncryptMsg(self, sReplyMsg, sTimeStamp, sNonce):
        """将内容加密并生成签名
        @param sReplyMsg: 内容
        @param sTimeStamp: 时间戳
        @param sNonce: 随机字符串
        @return: 加密后的内容
        """
        try:
            # 加密
            encrypt = self.pc.encrypt(sReplyMsg, self.receiveid)
            if encrypt is None:
                return -1, "加密失败"
            
            # 生成签名
            signature = SHA1.getSHA1(self.token, sTimeStamp, sNonce, encrypt.decode())
            
            # 生成发送的xml
            response = {
                "Encrypt": encrypt.decode(),
                "MsgSignature": signature,
                "TimeStamp": sTimeStamp,
                "Nonce": sNonce
            }
            return 0, self._gen_xml(response)
        except Exception as e:
            logger.exception(f"加密消息失败: {e}")
            return -1, "加密消息失败"

    def _gen_xml(self, data):
        """生成xml格式字符串
        @param data: 参数字典
        @return: xml格式字符串
        """
        xml = "<xml>\n"
        for key, value in data.items():
            xml += f"<{key}><![CDATA[{value}]]></{key}>\n"
        xml += "</xml>"
        return xml 