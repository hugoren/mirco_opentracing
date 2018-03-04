###环境
1. python 3.5+

###功能
1. api 接收日志
2. tcp/udp 接收日志
3. 离线 接收日志
4. 日志以生产者模式在redis发布
5. 监控消费队列，防止队列爆掉


###使用说明
1. 开启api功能，启动app.py
2. 开启udp功能，启动service.py
3. 开启redis


###测试
1. 启动logback_udp_demo(客户端udp在线发送数据)
2. 启动udp服务端service.py
3. 启动client udp 发送数据