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
    li = li_type[0]

    li_vin_prlist = conn.execute("SELECT t1.vin,t1.pr_list FROM public.mj_pr_repository as t1 WHERE t1.type='%s'",li[0])
    print(li[0])
    # if len =1 no deal
    len_li_vin_prlist=len(li_vin_prlist)
    if(len_li_vin_prlist>=2):
        pr_list_same = []
        pr_list_temp1=li_vin_prlist[0][1].split('|')
        pr_list_temp2=li_vin_prlist[1][1].split('|')
        for pr_list_temp_iter in pr_list_temp1:
            if pr_list_temp_iter in pr_list_temp2:
                pr_list_same.append(pr_list_temp_iter)
        if(len_li_vin_prlist>2):
            n=2
            while( n < len_li_vin_prlist):
                pr_list_temp=li_vin_prlist[n][1].split('|')
                for pr_list_temp_iter in pr_list_same:
                    if pr_list_temp_iter in pr_list_temp:
                        pass
                    else:
                        pr_list_same.remove(pr_list_temp_iter)
                n=n+1
        print(pr_list_same)

        templist=[]
        n=0
        while(n<len_li_vin_prlist):
            templist=li_vin_prlist[n][1].split('|')
            for pr_list_same_temp in pr_list_same:
                if pr_list_same_temp in templist:
                    templist.remove(pr_list_same_temp)
            pr_list_result=(''.join(map(list_con,templist))).strip('|')
            print(pr_list_result)
            print(li_vin_prlist[n][0])
            result=conn.execute("UPDATE public.mj_pr_repository  SET pr_list='%s' WHERE vin='%s'" % (pr_list_result,li_vin_prlist[n][0]))
            print(result)
            n+=1






