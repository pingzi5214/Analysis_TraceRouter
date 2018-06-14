# Analysis_TraceRouter
根据路由命令解析出来全网的最佳路由结果

描述： 在Cisco机型在进行下发show bgp命令的时候会显示当前当前机器中储存的所有的下一跳信息，
其中包含了最优的信息，显示的行数过多，需要在其中分析出来最优路由是那个，进行一个入库总结
在设备上执行show bgp的命令，解析出每段Network中最优的Next Hop的值，
机器返回信息如下所示，
Network          Next Hop            Metric LocPrf Weight Path
*>i x.x.x.x/24   xxx.xxx.xxx.xxx      0     xxx      0     xxxxxxxxxxxxxxxx
* i              xxx.xxx.xxx.xxx      0     xxx      0     xxxxxxxxxxxxxxxx
