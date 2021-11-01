# db 配置
# 用于记录摄像头的回放视频地址、历史警告信息等
# 目前还没使用 db 记录，所以如果想换成 mysql 也行
SQLALCHEMY_DATABASE_URI = "sqlite:////root/ai_server/config/test.db"

# oss 配置 [kaijie: 需要吗？要不就直接存服务器本地然后 nginx 作为文件服务器？]
# 用于保存视频、截图信息

# 这里用于控制 frame_buf 的缓冲区大小，
# 由于不清楚 frame_buf 的消费者的处理能力，
# 所以不会开无限大小，而是最多 1 / si * frame_buf_time_in_sec 张
# 也即最多缓冲 frame_buf_time_in_sec 时间的采样帧
# P.S. si 指的是 sampling interval 即采样间隔，以秒为单位
# 如果 0.1s 取 1 帧，也就是 1 秒取 10 帧，所以缓冲区为 10 * 10 为 100 帧
frame_buf_time_in_sec = 10 # 单位为秒

# 录视频的时候，如果 record_duration 秒的时间内没有检测结果，
# 则当前视频此时结尾，下一帧有检测结果的时候开始写到新视频文件
record_duration = 4 # 单位为秒

# 告警服务器
ALARM_SERVER_URL = "http://127.0.0.1:8888"