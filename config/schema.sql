-- TODO:
-- 就不考虑用户登录之类的了，目前的思路是
-- 每台摄像头的序列号作为唯一标识符 sn
-- 随后数据库中记录着不该摄像头的历史记录
-- 其中历史记录是细分为 某种模型(model)采用的算法(algorithm) 下的检测记录，也就是两个维度
-- 这里的算法说的就是场景的意思
-- 所以，根据 (sn, model, algo) 可以找到某场景下的历史记录
-- 根据 sn 可以找到该摄像头采用的所有模型下所有场景的历史记录
-- 也就是不区分用户是谁，也不区分其历史的 ip 地址等等

-- 目标监测模型表
CREATE TABLE `models`;
CREATE TABLE `models` (
    `id` INT UNSIGNED AUTO_INCREMENT,
    `model` VARCHAR(200) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 算法表（场景表）
-- 对于每种模型，都用有其在不同算法场景下的权重文件
-- /pts/model/algorithm.pt
CREATE TABLE `algorithms`;
CREATE TABLE `algorithms` (
    `id` INT UNSIGNED AUTO_INCREMENT,
    `algorithm` VARCHAR(200) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 
DROP TABLE IF EXISTS `records`;
CREATE TABLE `records` (
    `id` INT UNSIGNED AUTO_INCREMENT,
    `sn` VARCHAR(200) NOT NULL,
    `model` INT NOT NULL,
    `algorithm` INT NOT NULL,
    `record_date` TIMESTAMP NOT NULL,
    `record_path` VARCHAR(2038) NOT NULL,
    `image_path` VARCHAR(2038) NOT NULL,
    PRIMARY KEY (`id`),
) ENGINE=InnoDB DEFAULT CHARSET=utf8;