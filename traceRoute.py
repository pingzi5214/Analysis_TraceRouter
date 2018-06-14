#!/usr/bin/env Python
# -*- coding:UTF-8 -*-
import telnetlib, time, datetime
import re, cx_Oracle, os


# 当前类是Telnet连接类
class Telnet(object):
    def __init__(self, device_name, username, password, delay=5, port=23):
        self.device_name = device_name  # 连接驱动名
        self.username = username  # 连接用户名
        self.password = password  # 连接密码
        self.delay = float(delay)  # 设置相应等待延迟
        self.port = int(port)  # 端口号
        self.access = None
        self.endFlag = None
        self.moreFlag = '(\-)+( |\()?[Mm]ore.*(\)| )?(\-)+'

    def connect(self):
        result = None
        try:
            self.access = telnetlib.Telnet(self.device_name, self.port, timeout=10)
            login_prompt = self.access.expect(["Username:", "login:"], self.delay)
            self.access.write(self.username + "\n")
            password_prompt = self.access.expect(["Password:"], self.delay)
            self.access.write(self.password + "\n")
            isLog = self.access.expect(["#", ">"], self.delay)
            if '#' in isLog[2] or '>' in isLog[2]:
                result = self.access
            else:
                result = None
        except (Exception) as e:
            print(e)
            result = None

        if result != None:
            self.access.write('\n')
            time.sleep(0.1)
            message = self.access.expect(['#', '>'], 2)
            message = message[2].replace('\r', '')
            message = message.replace('\n', '')
            self.endFlag = message

        return result

    def close(self):
        self.access.write('quit' + '\n')
        return self.access.close()

    def command(self, command, time_delay=60):
        self.access.write(command + '\n')
        time.sleep(0.1)
        message = self.access.expect([r'%s' % self.moreFlag, self.endFlag], time_delay)  # 这是修改的地方
        # 0 完全接收
        # -1 超时
        result = message[2]
        result = result.replace(' --More--', '')
        result = result.replace('\r', '')

        f = open('show_bgp.log', 'w')
        f.write(result)
        f.flush()
        f.close()

        if message[0] == 0:
            self.getMore()
        elif message[0] == 1:
            pass
        elif message[0] == -1:
            # Recvive timeout
            result = result + '\t Recvive timeout'
        # print('-------------------------------------------------------')
        # print('command:' + command + '\n')
        # print('message:' + result)
        # print('-------------------------------------------------------')
        return result

    def getMore(self):
        result = ''
        f = open('show_bgp.log', 'a')
        try:
            while True:
                self.access.write(' ')
                i = self.access.expect([r'%s' % self.moreFlag, self.endFlag], timeout=10)
                # Get result
                temp = i[-1]
		# 去除影响的部分
                temp = temp.replace(' --More--', '')
                temp = temp.replace(' --More-', '')
                temp = temp.replace('-', '')
                temp = temp.replace('\r', '')
                temp = temp.replace(' \x08\x08\x08\x08\x08\x08\x08\x08\x08        \x08\x08\x08\x08\x08\x08\x08\x08\x08',
                                    '')
                temp = temp.replace('     Network          Next Hop            Metric LocPrf Weight Path\n', '')
                # print('++++++++++++++++++++++++++++++++++++++++++++++++')
                # print(temp)
                # print('++++++++++++++++++++++++++++++++++++++++++++++++')
                f.write(temp)
                f.flush()
                # result += temp
                if i[0] == 1:
                    break
        except (Exception) as e:
            print(e)
        finally:
            f.close()
        # return result


sssssssssss = datetime.datetime.now()

device = Telnet(device_name='device_ip', username='xxxxxxxxxxxxxxxxxxxxx', password='xxxxxxxxxxxxxxxxxxxxx')
if device.connect():
    device.command('show bgp')
    device.close()

##################################################################################################


f = open('show_bgp.log', 'r')
f.readline()
f.readline()
f.readline()
f.readline()
f.readline()
f.readline()
f.readline()
f.readline()
f.readline()
# iprouteList = list()

findIp_group = open('show_bgp_2.log', 'w')
while True:
    line = f.readline()
    if line:
        # 查看当前行和下一行是否关联
        relgx = r' *(>| )i (\d+).(\d+).(\d+).(\d+)/(\d+)\n'
        findRelgx = re.findall(relgx, line)
        if findRelgx:  # 判断是不是超长了，如果超长了，就要特殊处理
            line2 = f.readline()  # 继续读取下一行
            line = line.replace('\n', '')
            line = line + line2
        # 找出当前这行所有信息
        relgxSix = r' *(>| )i (.+?| +)( +)(.+?)( +)(\d+ | +)( +)(\d+)( +)(\d) (.+?)\n'
        findAllMessage = re.findall(relgxSix, line)
        if len(findAllMessage) != 0:
            findAllMessage = findAllMessage[0]
            # Network  Next Hop  Metric  LocPrf  Weight  Path
            is_BestFlag = findAllMessage[0]
            is_Network = findAllMessage[1]
            is_NextHop = findAllMessage[3]
            is_Metric = findAllMessage[5]
            is_LocPrf = findAllMessage[7]
            is_Weight = findAllMessage[9]
            is_Path = findAllMessage[10]
            if is_Network.strip() != '' or is_BestFlag == '>':
                print(line)
                findIp_group.write(line)
    else:
        break
f.close()
findIp_group.close()

##########################################################################################################################


f = open('show_bgp_2.log', 'r')
ff = open('show_bgp_3.log', 'w')
conn = cx_Oracle.connect('xxxx/xxxx@IP_Address/xxxxxxx')  # 用自己的实际数据库用户名、密码、主机ip地址 替换即可
curs = conn.cursor()
list_line = list()
try:
    while True:
        line = f.readline()
        if line:
            relgxSix = r' *(>| )i (.+?| +)( +)(.+?)( +)(\d+ | +)( +)(\d+)( +)(\d) (.+?)\n'
            findAllMessage = re.findall(relgxSix, line)
            if len(findAllMessage) != 0:
                findAllMessage = findAllMessage[0]
                # Network  Next Hop  Metric  LocPrf  Weight  Path
                is_BestFlag = findAllMessage[0]
                is_Network = findAllMessage[1]
                is_NextHop = findAllMessage[3]
                is_Metric = findAllMessage[5]
                is_LocPrf = findAllMessage[7]
                is_Weight = findAllMessage[9]
                is_Path = findAllMessage[10]
                if is_BestFlag != '>':
                    line = f.readline()
                    if line:
                        findAllMessage = re.findall(relgxSix, line)
                        if len(findAllMessage) != 0:
                            findAllMessage = findAllMessage[0]
                            is_BestFlag = findAllMessage[0]
                            is_NextHop = findAllMessage[3]
                            is_Metric = findAllMessage[5]
                            is_LocPrf = findAllMessage[7]
                            is_Weight = findAllMessage[9]
                            is_Path = findAllMessage[10]

                temp = is_BestFlag + '\t' + is_Network + '\t' + is_NextHop + '\t' + is_Metric + '\t' + is_LocPrf + '\t' + is_Weight + '\t' + is_Path + '\r'
                ff.write(temp)
                print(str(temp))
                list_line.append((is_Network, is_NextHop, is_Metric, is_LocPrf, is_Weight, is_Path))
                if len(list_line) > 10000:
                    # 执行批量插入
                    curs.executemany(
                        'insert into ctg_glb_route(NETWORK,NEXT_HOP,METRIC,LOC_PRF,WEIGHT,PATH)  values(:1,:2,:3,:4,:5,:6)',
                        list_line)
                    # 提交事务
                    conn.commit()
                    list_line = list() # 清空list
        else:
            break
    # 执行批量插入
    curs.executemany(
        'insert into ctg_glb_route(NETWORK,NEXT_HOP,METRIC,LOC_PRF,WEIGHT,PATH)  values(:1,:2,:3,:4,:5,:6)', list_line)
    # 提交事务
    conn.commit()
except (BaseException) as e:
    print(e)
finally:
    # os.remove('show_bgp.log')
    # os.remove('show_bgp_2.log')
    # os.remove('show_bgp_3.log')
    curs.close()
    conn.close()
eeeeeeeeee = datetime.datetime.now()
print(str((eeeeeeeeee - sssssssssss).seconds))
