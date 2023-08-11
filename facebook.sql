CREATE TABLE `fb_ad_country` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '国家ID',
  `country_code` varchar(255) DEFAULT '' COMMENT '国家简略代码',
  `country` varchar(255) DEFAULT '' COMMENT '国家',
  `is_crawling` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否需要爬取 1:未知 2:需要爬取 3:不需要爬取',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `updated_at` datetime DEFAULT NULL COMMENT '修改时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='facebook国家表';

CREATE TABLE `fb_ad_data` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '广告ID',
  `advertiser` varchar(128) DEFAULT '' COMMENT '广告商',
  `ad_content` varchar(4096) DEFAULT '' COMMENT '广告内容',
  `advertiser_url` varchar(512) DEFAULT '' COMMENT '广告商品url',
  `advertiser_domain` varchar(128) DEFAULT '' COMMENT '独立站url',
  `keyword` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '' COMMENT '搜索到这个广告的关键字',
  `country` varchar(255) DEFAULT '' COMMENT '广告投放国家',
  `is_jewelry` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否首饰站 0: 待判定 1:是 2:不是',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `updated_at` datetime DEFAULT NULL COMMENT '修改时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_url_domain` (`advertiser_url`,`advertiser_domain`)
) ENGINE=InnoDB AUTO_INCREMENT=108 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='facebook广告数据表';


CREATE TABLE `fb_ad_keyword` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '关键字ID',
  `keyword` varchar(255) DEFAULT '' COMMENT '关键字',
  `category` tinyint(1) DEFAULT NULL COMMENT '关键字分类 1:头(发)饰 2:项链 3:手(脚)镯 4:戒指 5:项链 6:耳(钉)环 7:身体首饰 8:胸针 9:其他',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '用户状态 1:未知 2:有效 3:无效',
  `is_crawling` tinyint DEFAULT '1' COMMENT '是否需要爬取 1:未知 2:需要爬取 3:不需要爬取',
  `page` int DEFAULT '20' COMMENT '关键字爬取数据页数',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `updated_at` datetime DEFAULT NULL COMMENT '修改时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='facebook关键字表';


CREATE TABLE `fb_ad_user` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(64) DEFAULT '' COMMENT '用户',
  `password` varchar(64) DEFAULT '' COMMENT '密码',
  `secret` varchar(128) DEFAULT '' COMMENT '二验码',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '用户状态 1:未知 2:可用 3:不可用',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `updated_at` datetime DEFAULT NULL COMMENT '修改时间',
  `deleted_at` datetime DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='facebook用户表';

CREATE TABLE `fb_filter_domain` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `domain` varchar(128) DEFAULT NULL COMMENT '域名',
  `rule` varchar(64) DEFAULT '' COMMENT '规则 全匹配:eq 模糊匹配:like',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '用户状态 1:启用 2:停用',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='facebook过滤域名表';