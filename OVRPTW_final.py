from gurobipy import *
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = ['Times New Roman']
plt.rcParams['font.size'] = 15


class Data:  # 数据类
    customerNum = 0  # 客户数量
    nodeNum = 0  # 点数量
    vehicleNum = 0  # 车辆数
    capacity = 0  # 车辆容量
    cor_X = []  # x坐标
    cor_Y = []  # y坐标
    demand = []  # 客户需求
    serviceTime = []  # 服务时间
    readyTime = []  # 最早时间窗
    dueTime = []  # 最晚时间窗
    disMatrix = [[]]  # 距离矩阵


# 读取数据函数
def readData(data, path, customerNum):
    data.customerNum = customerNum  # 客户数量
    data.nodeNum = customerNum + 2  # 节点数量
    f = open(path, 'r')  # ‘r’以只读方式打开文件。文件的指针将会放在文件的开头。这是默认模式。
    lines = f.readlines()  # 读取行数据，readlines() 方法用于读取所有行(直到结束符 EOF)并返回列表
    count = 0  # 从0开始计数
    # 读取信息
    for line in lines:
        count = count + 1  # 计数+1
        if (count == 5):  # 如果计数=5，第5行为车辆数和车辆容量
            line = line[:-1].strip()  # 默认情况下,函数strip()将删除字符串开头和结尾的空格,并返回前后不带空格的相同字符串。
            str = re.split(r" +", line)  # 字符分割
            data.vehicleNum = int(str[0])  # 第一个字符为车辆数
            data.capacity = float(str[1])  # 第二个字符为车辆容量
        elif (count >= 10 and count <= 10 + customerNum):  # 10行后为具体信息
            line = line[:-1]
            str = re.split(r" +", line)
            data.cor_X.append(float(str[2]))  # 为什么是2？ 因为存在空格
            data.cor_Y.append(float(str[3]))
            data.demand.append(float(str[4]))
            data.readyTime.append(float(str[5]))
            data.dueTime.append(float(str[6]))
            data.serviceTime.append(float(str[7]))

    # 信息获取完毕
    data.cor_X.append(data.cor_X[0])  # X坐标
    data.cor_Y.append(data.cor_Y[0])  # Y坐标
    data.demand.append(data.demand[0])  # 顾客需求
    data.readyTime.append(data.readyTime[0])  # 左时间窗，开始时间
    data.dueTime.append(data.dueTime[0])  # 右时间窗，结束时间
    data.serviceTime.append(data.serviceTime[0])  # 服务时间

    # 计算距离矩阵
    data.disMatrix = [([0] * data.nodeNum) for p in range(data.nodeNum)]  # 初始化距离矩阵的维度,防止浅拷贝
    # data.disMatrix = [[0] * nodeNum] * nodeNum]; 这个是浅拷贝，容易重复
    for i in range(0, data.nodeNum):
        for j in range(0, data.nodeNum):
            temp = (data.cor_X[i] - data.cor_X[j]) ** 2 + (data.cor_Y[i] - data.cor_Y[j]) ** 2
            data.disMatrix[i][j] = math.sqrt(temp)
            #             if(i == j):
            #                 data.disMatrix[i][j] = 0;
            # print("%6.2f" % (math.sqrt(temp)), end = " ");
    return data


def printData(data):
    print("下面打印数据\n")
    print("vehicle number = %4d" % data.vehicleNum)
    print("vehicle capacity = %4d" % data.capacity)
    for i in range(len(data.demand)):
        print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}'.format(data.cor_X[i], data.cor_Y[i], data.demand[i], data.readyTime[i],
                                                    data.dueTime[i], data.serviceTime[i]))
    print("-------距离矩阵-------\n")
    for i in range(data.nodeNum):
        for j in range(data.nodeNum):
            # print("%d   %d" % (i, j));
            print("%6.2f" % (data.disMatrix[i][j]), end=" ")  # 保留2位小数
        print()


# In[1]:

# reading data调用上面两个函数
data = Data()  # 对象实例化
# path = r'C:\Users\hsingluLiu\eclipse-workspace\PythonCallGurobi_Applications\VRPTW\c101.txt'
path = 'D:\pycharm\毕业论文\solomon_25\C101.txt'
customerNum = 25
readData(data, path, customerNum)
# data.vehicleNum = 3
printData(data)

# In[2]:
# # Build and solve VRPTW
BigM = 100000
'''创建模型'''
model = Model('OVRPTW')
# model.Params.IntFeasTol = 1e-9

x = {}  # 集合
s = {}

# 定义变量，变量以字典存储，x={(0, 1, 0): <gurobi.Var 车辆0从节点0到节点1 (value 0.0)>},
# key=(0, 1, 0),x[(0, 1, 0)]=<gurobi.Var 车辆0从节点0到节点1 (value 0.0)>,x[(0, 1, 0).x]=0
for i in range(data.nodeNum):
    for k in range(data.vehicleNum):
        name = 's_' + str(i) + '_' + str(k)  # str()函数，转化为字符格式
        '''s[i,k]到达时间'''
        s[i, k] = model.addVar(0  # 下界
                               , 1500  # 上界
                               , vtype=GRB.CONTINUOUS  # 连续变量
                               , name=name)
        for j in range(data.nodeNum):
            if (i != j):
                name = '车辆' + str(k) + '从节点' + str(i) + '到节点' + str(j)
                '''决策变量'''
                x[i, j, k] = model.addVar(vtype=GRB.BINARY  # 0-1变量
                                          , name=name)

'''更新模型'''
model.update()

# In[3]:
'''定义目标函数ok'''
obj = LinExpr(0)  # 线性表达式构造函数
for i in range(data.nodeNum):  # i属于N
    for k in range(data.vehicleNum):  # k属于K
        for j in range(1, data.customerNum + 1):  # j属于C
            if (i != j):
                obj.addTerms(data.disMatrix[i][j],
                             x[i, j, k])  # 向线性表达式中添加新项。addTerms adds an array of new terms at once.
# print(obj)
'''目标函数'''
model.setObjective(obj, GRB.MINIMIZE)

'''增加约束条件'''
# 定义约束一  车辆从仓库出发 sum(x[0][j][k]=1)
for k in range(data.vehicleNum):  # k属于K
    lhs = LinExpr(0)
    for j in range(1, data.customerNum + 1):  # j属于C
        if (j != 0):
            lhs.addTerms(1, x[data.customerNum + 1, j, k])
    model.addConstr(lhs <= 1, name='vehicle_depart_' + str(k))

# for i in range(1, data.nodeNum - 1):
#     lhs = LinExpr(0)
#     for j in range(data.nodeNum):
#         if(i != j):
#             for k in range(data.vehicleNum):
#                 lhs.addTerms(1, x[i,j,k])
#     for h in range(data.nodeNum):
#         if (i != h):
#             for k in range(data.vehicleNum):
#                 lhs.addTerms(-1, x[h, i, k])
#     model.addConstr(lhs == 0, name= 'flow_conservation_' + str(i))

# 定义约束二 流平衡 sum(x[i][j][k])=sum(x[j][i][k]) ok
for k in range(data.vehicleNum):  # 任意k属于K
    for h in range(1, data.customerNum + 1):
        expr1 = LinExpr(0)
        expr2 = LinExpr(0)
        for i in range(data.nodeNum):
            if (h != i):
                expr1.addTerms(1, x[i, h, k])

        for j in range(data.nodeNum):
            if (h != j):
                expr2.addTerms(1, x[h, j, k])

        model.addConstr(expr1 >= expr2, name='flow_conservation_' + str(i))
        expr1.clear()
        expr2.clear()  # 将线性表达式设置为0

# 定义约束三 车辆不返回仓库 sum(x[j][n+1][k]=1)
for k in range(data.vehicleNum):
    lhs = LinExpr(0)
    for j in range(data.nodeNum - 1):
        if (j != 0):
            lhs.addTerms(1, x[j, data.customerNum + 1, k])
    model.addConstr(lhs == 0, name='vehicle_depart_' + str(k))

# 定义约束四 每个客户仅服务一次 sum(x[i][j][k])=1
for j in range(1, data.customerNum + 1):
    lhs = LinExpr(0)
    for k in range(data.vehicleNum):
        for i in range(data.nodeNum):
            if (i != j):
                lhs.addTerms(1, x[i, j, k])
    model.addConstr(lhs == 1, name='customer_visit_' + str(i))

# 任意车辆不从仓库到仓库
for k in range(data.vehicleNum):
    model.addConstr(x[0, data.customerNum + 1, k] == 0)

# 定义约束五 时间窗约束
for k in range(data.vehicleNum):
    for i in range(data.nodeNum):
        for j in range(data.nodeNum):
            if (i != j):
                model.addConstr(s[i, k] + data.disMatrix[i][j] + data.serviceTime[i] - s[j, k]
                                - BigM + BigM * x[i, j, k] <= 0, name='time_windows_')

# 定义约束六 到达时间不违反时间窗 e[i]<=s[i]<=l[i]
for i in range(1, data.nodeNum - 1):
    for k in range(data.vehicleNum):
        model.addConstr(data.readyTime[i] <= s[i, k], name='ready_time')
        model.addConstr(s[i, k] <= data.dueTime[i], name='due_time')

# 定义约束七 载重约束
for k in range(data.vehicleNum):
    lhs = LinExpr(0)  # lhs：Left-hand side for the new constraint.
    for j in range(1, data.customerNum + 1):
        for i in range(data.nodeNum):
            if (i != j):
                lhs.addTerms(data.demand[i], x[i, j, k])
    model.addConstr(lhs <= data.capacity, name='capacity_vehicle' + str(k))

# 导出模型 写入lp文件
model.write('VRPTW.lp')

'''优化模型'''
model.optimize()

'''错误模型检查'''
# model.computeIIS()
# model.write("model1.ilp")

# 打印结果
print("\n\n-----optimal value-----")
print(model.ObjVal)

# print(x.keys())
# print(x.values())
# print(type(x.values()))
for key in x.keys():
    if (x[key].x > 0):
        print(x[key].VarName + ' = ', x[key].x)

'''字符转为list'''
zifu = []
for key in x.keys():
    if (x[key].x > 0):
        zifu.append(x[key].VarName)
zifu.sort()
print(zifu)

'''提取数字'''
import re
fenge = [([]) for i in range(data.customerNum)]
for char in range(data.customerNum):
    a = zifu[char]
    number = list(filter(str.isdigit, a))
    fenge[char] = re.findall(r"\d+\.?\d*", a)
print('提取数字',fenge)

'''提取车辆号'''
chehao = []
for i in range(data.customerNum):
    if fenge[i][0] not in chehao:
        chehao.append(fenge[i][0])
print('车牌号：',chehao)

'''路径分割（手动调节）'''
route = [([]) for i in range(len(chehao))]
for i in range(data.customerNum):
    if fenge[i][0] == chehao[0] : route[0].append(fenge[i])
    if fenge[i][0] == chehao[1] : route[1].append(fenge[i])
    if fenge[i][0] == chehao[2] : route[2].append(fenge[i])
    # if fenge[i][0] == chehao[3] : route[3].append(fenge[i])
    # if fenge[i][0] == chehao[4] : route[4].append(fenge[i])
    # if fenge[i][0] == chehao[5] : route[5].append(fenge[i])
    # if fenge[i][0] == chehao[6] : route[6].append(fenge[i])
    # if fenge[i][0] == chehao[7] : route[7].append(fenge[i])
    # if fenge[i][0] == chehao[8] : route[8].append(fenge[i])
    # if fenge[i][0] == chehao[9] : route[9].append(fenge[i])
print(route)

plt.figure(dpi=600)
for i in range(len(chehao)):
    '''路径连接'''
    s1 = route[i]
    r1 = ['0']
    count = 0
    while count < len(s1):
        for i in range(len(s1)):
            if s1[i][1] in r1 and s1[i][2] not in r1:
                r1.append(s1[i][2])
                # r1.remove(r1[i])
        count += 1

    r1 = [int(x) for x in r1]
    print(r1)

    x1,y1 = [],[]
    for i in r1:
        x1.append(data.cor_X[i])
        y1.append(data.cor_Y[i])
    plt.plot(x1,y1,marker='o',linewidth=0.8,markersize=5)

plt.scatter(data.cor_X[0],data.cor_Y[0],marker='*',color='red',s=200)

plt.xlabel('x_coord')
plt.ylabel('y_coord')

plt.show()

'''画图'''

#
# r1 = [26,13,17,18,19,15,16,14,12]
# r2 = [26,20,24,25,23,22,21]
# r3 = [26,5,3,7,8,10,11,9,6,4,2,1]
#

# x2,y2 = [],[]
# x3,y3 = [],[]
#

# for i in r3:
#     x3.append(data.cor_X[i])
#     y3.append(data.cor_Y[i])
# plt.plot(x3,y3,marker='o',color='blue',linewidth=0.8,markersize=5)
#
# for i in r1:
#     x1.append(data.cor_X[i])
#     y1.append(data.cor_Y[i])
# plt.plot(x1,y1,marker='o',color='red',linewidth=0.8,markersize=5)
#

