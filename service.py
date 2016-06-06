#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2015  Data Enlighten Technology (Beijing) Co.,Ltd


__author__ = 'Sunq'

from flask import Flask
from flask import request
from flask import jsonify
from flask import json
import Lib.Logger.log4py as log
from Server.parsemessage import MessageFormatter
import Server.const
from Server.config import Config
from Process import ProviderBase
import datetime
from Lib.Database.connection import PostgreSQLConnector
#import Process.nlpir.nlpir as nlp
import copy
import sys
from gevent import Timeout
from gevent import monkey
import gevent
from redis.sentinel import Sentinel
from Lib.SSO.sso import SSOAuth
import urllib.request
from urllib.error import URLError,HTTPError
import socket

app = Flask(__name__)
#monkey.patch_socket()

class HttpServer:

    def __init__(self):
        pass
        #self.provider = ProviderFactory()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        log.e('HttpServer was encountered the error')


def start_server():
    #app.run(host='120.25.227.122',port=8078)
    config = Config(Server.const.Config)
    app.run(host=config.ip_address,port=int(config.port), threaded=True) #需要用小写，因为configparser会转化为小写
    return

@app.route('/')
@app.route('/test')
def test():
    return app.send_static_file('test.html')


##暂时用全局函数,放入到HttpServer类里去,会遇到问题
@app.route('/getdata', methods=['POST', 'GET'])
def getdata():
    try:
        config = Config(Server.const.Config)
        log.d(request.method)
        log.d(request.remote_addr)
        pv_base = ProviderBase()
        msgfmter = MessageFormatter(get_request)
        t_req=datetime.datetime.now()

        '''
        gevent.sleep(0)
        timeout = gevent.Timeout(int(config.timeout))
        timeout.start()
        log.d('timeout = ' + config.timeout)
        '''

        result = {}
        log.d('VIN Code:[%s]' % msgfmter.VinCode)
        log.d('MaintenanceStationID Code:[%s]' % msgfmter.MaintenanceStationID)

        if len(msgfmter.VinCode.replace(' ','')) < 17:
            log.e("VIN's length was wrong..")
            dictMerged = {}
            dictMerged.update(msgfmter.build_HTTP_head())
            dictMerged['ResponseCode'] = '89'
            dictMerged['ResponseCodeDescription'] = 'VIN码长度不正确'
            return json.dumps(dictMerged)

        tables_brand_id = pv_base.select_brand_by_id(msgfmter.VinCode.upper())
        brand_id = ''
        if tables_brand_id is not None and len(tables_brand_id) > 0:
            brand_id = tables_brand_id[0]
            log.d('Brand:id = [%s],cls = [%s]' % (tables_brand_id[0],tables_brand_id[1]))
            res_check_user_auth = check_sso_auth(msgfmter.MaintenanceStationID, brand_id, msgfmter.TransactionType)
            log.d(res_check_user_auth)
        else:
            log.d('该品牌汽车暂不支持！')
            result['ResponseCode'] = '30'
            result['ResponseCodeDescription'] = '无法识别的汽车品牌'
            dictMerged = dict(result)
            dictMerged.update(msgfmter.build_HTTP_head())
            return json.dumps(dictMerged)

        #add for log on 01-20 start
        try:
            t_req=datetime.datetime.now()
            form = request.form.to_dict()
            args = request.args.to_dict()
            if (form == None or len(form)==0) and (args != None or len(args)>0):
                form=args
            saveLogIntoBaseDB('','request',json.dumps(form,ensure_ascii=False).replace("'","''"),t_req)
            sso_log(msgfmter.MaintenanceStationID, brand_id, msgfmter.TransactionType, 'request', json.dumps(form,ensure_ascii=False).replace("'", "''"), t_req)
        except Exception as e:
            log.e(e)
        #end

        if res_check_user_auth != '00':
            log.d('res_check_user_auth was failed！')
            result['ResponseCode'] = res_check_user_auth
            DescriptionList= {'50':'用户不存在',
                              '51':"用户已封号",
                              '52':"用户有效期失效",
                              '53':"用户无品牌查询权限",
                              '54':"用户查询品牌有效期失效",
                              '55':"用户此品牌查询已被封",
                              '56':"用户每天查询vin超过限定次数",
                              '57':"用户每天查询part超过限定次数",
                              '58':"用户查询vin总数超过限定次数",
                              '59':"用户查询part总数超过限定次数",
                              '60':"用户1小时内访问次数超过限定次数",
                              '61':"用户1天内访问次数超过限定次数",
                              '62':"用户1个月内访问次数超过限定次数"
                             }

            if res_check_user_auth in DescriptionList.keys():
                result['ResponseCodeDescription'] = DescriptionList[res_check_user_auth]
            else:
                result['ResponseCodeDescription'] = '用户没有权限访问'

            dictMerged = dict(result)
            dictMerged.update(msgfmter.build_HTTP_head())
            return json.dumps(dictMerged)

        if msgfmter.TransactionType == '01':
            #log.d('VIN Code:[%s]' % msgfmter.VinCode)


            if msgfmter.VinCode == 'SPECIAL_FOR_POLLING':
                dictMerged={'ResponseCode': '200'}
                return json.dumps(dictMerged)

            brand = pv_base.select_brand_by_vin( msgfmter.VinCode[:3].upper())

            if brand is not None and len(brand) > 0:
                log.d('Brand:[%s],[%s]' % (brand[0],brand[1]))
                verify_vin = getattr(load_model(brand[0]), "verify_vin")
                result = verify_vin(msgfmter.VinCode.upper())
                result['Brand'] = brand[1]
            else:
                log.d('该品牌汽车暂不支持！')
                result['ResponseCode'] = '30'
                result['ResponseCodeDescription'] = '无法识别的汽车品牌'



        elif msgfmter.TransactionType == '02':
            #nlp_list = nlp.MJJH_BZ_Info(msgfmter.PartNameCHN.upper())
            nlp_list = nlpir_parser(msgfmter.PartNameCHN.upper(), config.nlpserver, config.nlpserver_posrt)
            if nlp_list is not None and len(nlp_list) > 0:
                #if msgfmter.CarModeCode.isdigit()==False:  #开始为防止脏数据,后由于加入车型信息,注释掉
                #    raise Exception("CarModeCode was invalid digit.")
                li = msgfmter.CarModeCode.split(':')
                log.d('Brand:[%s]' % li[0])
                #log.d('VIN:[%s]'%msgfmter.VinCode.upper())
                find_parts_by_name = getattr(load_model(li[0]), "find_parts_by_name")
                result = find_parts_by_name(li[1], nlp_list, msgfmter.VinCode.upper())
                #加判断,一旦没有查到,清除方向再查询
                #added for log 01-22 start by Neo
                result['nlpir_result']=nlp_list
                #end

            else:
                log.d('[%s]无法识别的专业用语',msgfmter.PartNameCHN)
                result['ResponseCode'] = '20'
                result['ResponseCodeDescription'] = '无法识别的专业用语'

        elif msgfmter.TransactionType == '03':
            li = msgfmter.CarModeCode.split(':')
            log.d('Brand:[%s], CarGroupCode:[%s], PartBlockCode:[%s]' % (li[0],msgfmter.CarGroupCode,msgfmter.PartBlockCode))
            find_parts_by_index = getattr(load_model(li[0]), "find_parts_by_index")
            result = find_parts_by_index(li[1],msgfmter.CarGroupCode,msgfmter.PartBlockCode, msgfmter.VinCode.upper())
        dictMerged=dict(result)
        dictMerged.update(msgfmter.build_HTTP_head())

    except Timeout as t:
        log('Timeout occurred.!!')
        #if t is not timeout:
        #    log('Timeout occurred.!!')
        #else:
        #    log.e('Timeout occurred.but timeout was not define.')
        dictMerged={}
        dictMerged.update(msgfmter.build_HTTP_head())
        dictMerged['ResponseCode'] = '88'
        dictMerged['ResponseCodeDescription'] = '服务器操作超时'

    except Exception as e:
        log.e(e)
        dictMerged={}
        dictMerged.update(msgfmter.build_HTTP_head())
        dictMerged['ResponseCode'] = '80'
        dictMerged['ResponseCodeDescription'] = '无效的异常码'
        #add for log on 01-19 start
        req_str=str(request.values);
        if len(req_str)>700:
            req_str=req_str[0:700]+"..."
        str_e="Error {0}".format(str(e.args[0])).encode("utf-8")
        if len(str_e)>60:
            str_e=str_e[0:60]+"..."
        log_result=copy.deepcopy(dictMerged);
        log_result['Exception']=str_e;
        saveLogIntoExp_ErrDB('',req_str.replace("'","''"),'Exception',t_req ,str(log_result).replace("'","''"));
        #end

    #add for log on 01-20 start
    log.d ('getdata was end')
    log.d(request.remote_addr)
    try:
        encodedjson = json.dumps(dictMerged,ensure_ascii=False)
        log_result=json.loads(encodedjson);
        if 'nlpir_result' in dictMerged:
            dictMerged.pop('nlpir_result');
        if 'NoShortnumMaptbl' in dictMerged:
            dictMerged.pop('NoShortnumMaptbl');
        #if 'PartNumberList' in dictMerged:
            #partList=list(dictMerged['PartNumberList']);
            #if len(partList)>0:
                #for part in  partList:
                    #if 'PicPath' in part:
                        #part.pop('PicPath');#0331-retain pic info
        if 'StructuredPartNameList' in log_result:
                log_result.pop('StructuredPartNameList');
        if 'PartNumberList' in log_result:
            partList=list(log_result['PartNumberList']);
            if len(partList)>0:
                for part in  partList:
                    if 'ImageFile' in part:
                        part.pop('ImageFile');
                    if 'CarModeCode'in part:
                        part.pop('CarModeCode');
                    if 'PartNumberIndexRef'in part:
                        part.pop('PartNumberIndexRef');
                    if 'CarGroupCode'in part:
                        part.pop('CarGroupCode');
            if  len(str(partList))>2500:# temp solution, remove it in kafka
                partList=partList[0]
            log_result['PartNumberList']= partList ;
        if 'nlpir_result'in log_result:
            #nlpir_atoms= nlp.segmentForLog(msgfmter.PartNameCHN.upper());
            nlpir_atoms = ''
            log_result['inputwords'] = msgfmter.PartNameCHN;
            log_result['nlpir_atoms']= nlpir_atoms
        t_resp=datetime.datetime.now()
        saveLogIntoBaseDB('','response',json.dumps(log_result,ensure_ascii=False).replace("'","''"),t_resp);
        sso_log(msgfmter.MaintenanceStationID, brand_id, msgfmter.TransactionType, 'response', json.dumps(log_result,ensure_ascii=False).replace("'", "''"), t_req)
        #end
    except Exception as e:
        log.e(e)
    log.d(json)
    return json.dumps(dictMerged)

def nlpir_parser(standard_name_chn, server_ip, server_port):
    result_list = []
    try:
        p = {'inputwords': standard_name_chn}
        url_values = urllib.parse.urlencode(p)
        url_values = url_values.encode(encoding='UTF8')
        req = urllib.request.Request('http://' + server_ip + ':' + server_port + "/nlpirService",url_values)
        res = urllib.request.urlopen(req, timeout=80)
        response = res.read()

        if response is not None and len(response) > 0:
            response_list = response.decode('utf-8').split('##')
            if len(response_list) == 3 and len(response_list[2]) != '':
                chn_name_list = response_list[2].split('&&')
                result_list = [x for x in chn_name_list if len(x) > 0]
    except socket.timeout as e:
        log.e(e)
    except HTTPError as e:
        log.d(e)
    except URLError as e:
        log.d(e)
    except Exception as ex:
        log.e(ex)
    return result_list

#add for log on 01-20 start
def saveLogIntoBaseDB(user_name,data_type,data_content,log_time):
    try:
        con = PostgreSQLConnector()
        sql="insert into mj_log_base_info (user_name,data_type,data_content,log_time ,flag)\
             values('%s','%s','%s','%s','0')"%(user_name,data_type,data_content,log_time );
        con.executeUpdateDB(sql);
    except Exception as e:
        con.rollback()
        log.e(e)

def saveLogIntoExp_ErrDB(userId,req_content,err_exp_type,t_req ,sys_err_exp_desc ):
    try:
        con = PostgreSQLConnector()
        sql="insert into mj_log_system_err_exp_info (user_id,request_content,err_exp_type,request_time,sys_err_exp_desc,flag)\
             values('%s','%s','%s','%s','%s','0')"%(userId,req_content,err_exp_type,t_req ,sys_err_exp_desc);
        con.executeUpdateDB(sql);
    except Exception as e:
        con.rollback()
        log.e(e)
#end

def load_model(brand):
    module_name = "Process.%s.provider"% brand
    __import__(module_name)
    pv_mod = sys.modules[module_name]
    cls = getattr(pv_mod, 'Provider')
    return cls()


def get_request( x):
    if request.method=="POST":
        return request.form.get(x,'ERROR')
    else:
        return request.args.get(x, '')


def check_sso_auth(user_id, brand_id, trans_type ):
    sentinel = Sentinel([('120.76.154.208', 26379)], socket_timeout=0.5)
    log.d(sentinel.discover_master('mymaster'))
    redis_obj = sentinel.master_for('mymaster', socket_timeout=0.1)

    db_obj = PostgreSQLConnector()
    sso_cls = SSOAuth(redis_obj,db_obj)
    return sso_cls.check_auth(user_id, brand_id, trans_type)


def sso_log(user_id, brand_id, trans_type, data_type,data_content,log_time):
    sentinel = Sentinel([('112.74.198.224', 26379)], socket_timeout=0.5)
    log.d(sentinel.discover_master('mymaster'))
    redis_obj = sentinel.master_for('mymaster', socket_timeout=0.1)

    db_obj = PostgreSQLConnector()
    sso_cls = SSOAuth(redis_obj,db_obj)
    return sso_cls.send_log(user_id, brand_id, trans_type, data_type,data_content,log_time)

if __name__ == '__main__':
    app.run(port=8080, threaded=True)