# 替换不规范的括号，全部换成中文括号
update financial_exchange set Xf_company_name=REPLACE(Xf_company_name,'(','（');
update financial_exchange set Gf_company_name=REPLACE(Gf_company_name,'(','（');
update financial_exchange set Xf_company_name=REPLACE(Xf_company_name,')','）');
update financial_exchange set Gf_company_name=REPLACE(Gf_company_name,')','）');
update ticket_bill set Gfmc=REPLACE(Gfmc,')','）');
update ticket_bill set Gfmc=REPLACE(Gfmc,'(','（');
update ticket_bill set Xfmc=REPLACE(Xfmc,')','）');
update ticket_bill set Xfmc=REPLACE(Xfmc,'(','（');

#更新exchangetype字段，注意改日期
#gf是岛内的，就是1，xf是岛内的，就是0, 两边都是岛内时以上游为准，即只要上游（xf）是岛内的exchangetype就等于0
UPDATE financial_exchange SET exchangetype=1 WHERE Gf_com_group=1 and exchange_date>'2019-01-01';
UPDATE financial_exchange SET exchangetype=0 WHERE Xf_com_group=1 and exchange_date>'2019-01-01' ;
UPDATE financial_exchange SET exchangetype=1 WHERE  Xf_company_name = '恒力石化（大连）炼化有限公司';

#更新产品名称和编码
DELETE FROM financial_exchange where Xf_company_name LIKE '%暂估%' or Gf_company_name LIKE '%暂估%';
UPDATE financial_exchange SET spec_id = CONCAT('0', spec_id) WHERE LENGTH(spec_id)=5;
UPDATE financial_exchange SET main_id = CONCAT('0', main_id) WHERE LENGTH(main_id)=5;
# 下面一行注意改年份，减少数据量
UPDATE financial_exchange f,ypt_goods_type y SET f.spec_name = y.path_name WHERE f.spec_id = y.path_code AND spec_name is NULL and y.level=2 AND f.exchange_date>'2019-01-01';
UPDATE financial_exchange SET year=LEFT(exchange_date,4) WHERE year is NULL;
UPDATE financial_exchange SET year=LEFT(add_time,4) WHERE year = '1970' or year = '0000';

#删除因调整格式而多出的冗余行
DELETE FROM financial_exchange where exchange_good ='' AND Sl is NULL AND Dj is NULL and Je <0.001 and year = 2019;
DELETE FROM ticket_bill where Spmc ='' AND Je <0.001 and Kprq >= '2019-01-01';
DELETE FROM financial_exchange where exchange_good ='' AND Je <0.001 and exchange_date >= '2019-01-01';

# 清空total表
TRUNCATE TABLE in_total;
# group by 报错
set @@GLOBAL.sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
# 导入新数据
# 1.统计各公司历年收入
INSERT INTO in_total(com_name,com_id,income,year)
SELECT Xfmc,Xf_id,ROUND(SUM(Je),2) 'income',LEFT(Kprq,4) 'year' FROM ticket_bill WHERE Xfmc IS NOT NULL AND LEFT(Kprq,1) = 2 GROUP BY Xfmc,LEFT(Kprq,4);
# 2.更新各公司历年支出
UPDATE in_total t,
(SELECT Gf_company_name,Gf_company_id,ROUND(SUM(Je),2) 'cost',year FROM financial_exchange WHERE Gf_company_name IS NOT NULL AND Gf_com_group=1
AND LEFT(year,1) = 2 GROUP BY Gf_company_name,year) a
SET t.cost = a.cost WHERE t.com_name = a. Gf_company_name AND t.year = a.year;
# 3.计算gmv gpm
UPDATE in_total SET gmv = income+cost;
UPDATE in_total SET gpm = income-cost;
UPDATE in_total SET gmv = income,gpm = income WHERE cost IS NULL;

# 清空in_com_relation表
TRUNCATE TABLE in_com_relation;
# 导入新数据
INSERT INTO in_com_relation(name,com_id,sy_name,sy_id,deal_type,Gmv,`year`)
SELECT Xfmc,Xf_id,Gfmc,Gf_id,0,ROUND(SUM(Je),2),'2020' FROM ticket_bill WHERE LEFT(Kprq,4) = '2020' GROUP BY Xfmc,Gfmc ORDER BY Xfmc;
INSERT INTO in_com_relation(name,com_id,sy_name,sy_id,deal_type,Gmv,`year`)
SELECT Gf_company_name,Gf_company_id,Xf_company_name,Xf_company_id,1,ROUND(SUM(Je),2),'2020' FROM financial_exchange WHERE `year` = '2020' and Xf_com_group = 0
AND Gf_com_group = 1 GROUP BY Xf_company_name,Gf_company_name ORDER BY Gf_company_name;

INSERT INTO in_com_relation(name,com_id,sy_name,sy_id,deal_type,Gmv,`year`)
SELECT Xfmc,Xf_id,Gfmc,Gf_id,0,ROUND(SUM(Je),2),'2019' FROM ticket_bill WHERE LEFT(Kprq,4) = '2019' GROUP BY Xfmc,Gfmc ORDER BY Xfmc;
INSERT INTO in_com_relation(name,com_id,sy_name,sy_id,deal_type,Gmv,`year`)
SELECT Gf_company_name,Gf_company_id,Xf_company_name,Xf_company_id,1,ROUND(SUM(Je),2),'2019' FROM financial_exchange WHERE `year` = '2019' and Xf_com_group = 0
AND Gf_com_group = 1 GROUP BY Xf_company_name,Gf_company_name ORDER BY Gf_company_name;

INSERT INTO in_com_relation(name,com_id,sy_name,sy_id,deal_type,Gmv,`year`)
SELECT Xfmc,Xf_id,Gfmc,Gf_id,0,ROUND(SUM(Je),2),'2018' FROM ticket_bill WHERE LEFT(Kprq,4) = '2018' GROUP BY Xfmc,Gfmc ORDER BY Xfmc;
INSERT INTO in_com_relation(name,com_id,sy_name,sy_id,deal_type,Gmv,`year`)
SELECT Gf_company_name,Gf_company_id,Xf_company_name,Xf_company_id,1,ROUND(SUM(Je),2),'2018' FROM financial_exchange WHERE `year` = '2018' and Xf_com_group = 0
AND Gf_com_group = 1 GROUP BY Xf_company_name,Gf_company_name ORDER BY Gf_company_name;

INSERT INTO in_com_relation(name,com_id,sy_name,sy_id,deal_type,Gmv,`year`)
SELECT Xfmc,Xf_id,Gfmc,Gf_id,0,ROUND(SUM(Je),2),'2017' FROM ticket_bill WHERE LEFT(Kprq,4) = '2017' GROUP BY Xfmc,Gfmc ORDER BY Xfmc;
INSERT INTO in_com_relation(name,com_id,sy_name,sy_id,deal_type,Gmv,`year`)
SELECT Gf_company_name,Gf_company_id,Xf_company_name,Xf_company_id,1,ROUND(SUM(Je),2),'2017' FROM financial_exchange WHERE `year` = '2017' and Xf_com_group = 0
AND Gf_com_group = 1 GROUP BY Xf_company_name,Gf_company_name ORDER BY Gf_company_name;

INSERT INTO in_com_relation(name,com_id,sy_name,sy_id,deal_type,Gmv,`year`)
SELECT Xfmc,Xf_id,Gfmc,Gf_id,0,ROUND(SUM(Je),2),'2016' FROM ticket_bill WHERE LEFT(Kprq,4) = '2016' GROUP BY Xfmc,Gfmc ORDER BY Xfmc;
INSERT INTO in_com_relation(name,com_id,sy_name,sy_id,deal_type,Gmv,`year`)
SELECT Gf_company_name,Gf_company_id,Xf_company_name,Xf_company_id,1,ROUND(SUM(Je),2),'2016' FROM financial_exchange WHERE `year` = '2016' and Xf_com_group = 0
AND Gf_com_group = 1 GROUP BY Xf_company_name,Gf_company_name ORDER BY Gf_company_name;

INSERT INTO in_com_relation(name,com_id,sy_name,sy_id,deal_type,Gmv,`year`)
SELECT Xfmc,Xf_id,Gfmc,Gf_id,0,ROUND(SUM(Je),2),'2015' FROM ticket_bill WHERE LEFT(Kprq,4) = '2015' GROUP BY Xfmc,Gfmc ORDER BY Xfmc;
INSERT INTO in_com_relation(name,com_id,sy_name,sy_id,deal_type,Gmv,`year`)
SELECT Gf_company_name,Gf_company_id,Xf_company_name,Xf_company_id,1,ROUND(SUM(Je),2),'2015' FROM financial_exchange WHERE `year` = '2015' and Xf_com_group = 0
AND Gf_com_group = 1 GROUP BY Xf_company_name,Gf_company_name ORDER BY Gf_company_name;

INSERT INTO in_com_relation(name,com_id,sy_name,sy_id,deal_type,Gmv,`year`)
SELECT Xfmc,Xf_id,Gfmc,Gf_id,0,ROUND(SUM(Je),2),'2014' FROM ticket_bill WHERE LEFT(Kprq,4) = '2014' GROUP BY Xfmc,Gfmc ORDER BY Xfmc;
INSERT INTO in_com_relation(name,com_id,sy_name,sy_id,deal_type,Gmv,`year`)
SELECT Gf_company_name,Gf_company_id,Xf_company_name,Xf_company_id,1,ROUND(SUM(Je),2),'2014' FROM financial_exchange WHERE `year` = '2014' and Xf_com_group = 0
AND Gf_com_group = 1 GROUP BY Xf_company_name,Gf_company_name ORDER BY Gf_company_name;

INSERT INTO in_com_relation(name,com_id,sy_name,sy_id,deal_type,Gmv,`year`)
SELECT Xfmc,Xf_id,Gfmc,Gf_id,0,ROUND(SUM(Je),2),'2013' FROM ticket_bill WHERE LEFT(Kprq,4) = '2013' GROUP BY Xfmc,Gfmc ORDER BY Xfmc;
INSERT INTO in_com_relation(name,com_id,sy_name,sy_id,deal_type,Gmv,`year`)
SELECT Gf_company_name,Gf_company_id,Xf_company_name,Xf_company_id,1,ROUND(SUM(Je),2),'2013' FROM financial_exchange WHERE `year` = '2013' and Xf_com_group = 0
AND Gf_com_group = 1 GROUP BY Xf_company_name,Gf_company_name ORDER BY Gf_company_name;

INSERT INTO in_com_relation(name,com_id,sy_name,sy_id,deal_type,Gmv,`year`)
SELECT Xfmc,Xf_id,Gfmc,Gf_id,0,ROUND(SUM(Je),2),'2012' FROM ticket_bill WHERE LEFT(Kprq,4) = '2012' GROUP BY Xfmc,Gfmc ORDER BY Xfmc;
INSERT INTO in_com_relation(name,com_id,sy_name,sy_id,deal_type,Gmv,`year`)
SELECT Gf_company_name,Gf_company_id,Xf_company_name,Xf_company_id,1,ROUND(SUM(Je),2),'2012' FROM financial_exchange WHERE `year` = '2012' and Xf_com_group = 0
AND Gf_com_group = 1 GROUP BY Xf_company_name,Gf_company_name ORDER BY Gf_company_name;

