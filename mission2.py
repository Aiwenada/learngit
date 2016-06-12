#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2015  Data Enlighten Technology (Beijing) Co.,Ltd


__author__ = 'ada'

import zgy.connectiontest as conntest

def list_con(str):
    return str+'|'

if __name__ == '__main__':
    conn = conntest.PostgreSQLConnector()
    #conn.connection("local")

    li_type = conn.execute("SELECT DISTINCT t1.type FROM public.mj_pr_repository as t1 ")

    for li in li_type:
        li_vin_prlist = conn.execute("SELECT t1.vin,t1.pr_list FROM public.mj_pr_repository as t1 WHERE t1.type='%s'",li[0])
        len_li_vin_prlist=len(li_vin_prlist)
        if(len_li_vin_prlist>=2):
            pr_list_same=[]
            pr_list_temp1=li_vin_prlist[0][1].split('|')
            if (len(pr_list_temp1)>=1):
                for pr_list_temp_iter in pr_list_temp1:
                    n=1
                    while(n<len_li_vin_prlist):
                        pr_list_temp=li_vin_prlist[n][1].split('|')
                        if pr_list_temp_iter in pr_list_temp:
                            n=n+1
                        else:
                            break
                    if n==len_li_vin_prlist:
                        pr_list_same.append(pr_list_temp_iter)
                print(li[0],pr_list_same)

                templist=[]
                m=0
                while(m<len_li_vin_prlist):
                    templist=li_vin_prlist[m][1].split('|')
                    for pr_list_same_iter in pr_list_same:
                        if pr_list_same_iter in templist:
                            templist.remove(pr_list_same_iter)
                    pr_list_result=(''.join(map(list_con,templist))).strip('|')
                    conn.executeUpdateDB("UPDATE public.mj_pr_repository  SET pr_list='%s' WHERE vin='%s'" , (pr_list_result,li_vin_prlist[m][0]))
                    m+=1
        else:
            print(li[0],'type only one record',li_vin_prlist[0][1].split('|'))





