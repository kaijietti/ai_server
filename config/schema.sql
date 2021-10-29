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
    `record_path` VARCHAR(2038) NOT NULL,
    `record_date` TIMESTAMP NOT NULL,
    PRIMARY KEY (`id`),
) ENGINE=InnoDB DEFAULT CHARSET=utf8;