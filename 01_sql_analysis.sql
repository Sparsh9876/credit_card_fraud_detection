-- ============================================================
--  CREATE TABLE
--  Match every column in the CSV exactly.
-- ============================================================

DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
    transaction_id            VARCHAR(20)     PRIMARY KEY,
    cardholder_name           VARCHAR(100)    NOT NULL,
    age                       SMALLINT        NOT NULL CHECK (age BETWEEN 18 AND 100),
    gender                    VARCHAR(10)     NOT NULL,
    transaction_amount        NUMERIC(10, 2)  NOT NULL,
    merchant_name             VARCHAR(150)    NOT NULL,
    merchant_category         VARCHAR(50)     NOT NULL,
    city                      VARCHAR(50)     NOT NULL,
    transaction_time          varchar(50)      NOT NULL,  
    international_transaction SMALLINT        NOT NULL CHECK (international_transaction IN (0,1)),
    card_present              SMALLINT        NOT NULL CHECK (card_present IN (0,1)),
    failed_attempts           SMALLINT        NOT NULL,
    fraud                     SMALLINT        NOT NULL CHECK (fraud IN (0,1))
);

select * from transactions;

-- Helpful indexes for faster queries

CREATE INDEX idx_fraud
ON transactions(fraud);

CREATE INDEX idx_category
ON transactions(merchant_category);

CREATE INDEX idx_city
ON transactions(city);

CREATE INDEX idx_amount
ON transactions(transaction_amount);

-- ============================================================
--  import csv file from import/export option 
-- ============================================================

-- ========
-- verify
-- ========
SELECT COUNT(*) AS total_rows FROM transactions;

-- ===================================================
-- data quality checks
-- ===================================================

-- check null values for every columnn
select 
sum(case when transaction_id     is null then 1 else 0 end) as null_txn_id,
sum(case when cardholder_name    is null then 1 else 0 end ) as null_name,
sum(case when age                is null then 1 else 0 end ) as  null_age,
sum(case when gender             is null then 1 else 0 end ) as null_gender,
sum(case when transaction_amount is null then 1 else 0 end ) as null_amount,
sum(case when merchant_name      is null then 1 else 0 end ) as null_merchant,
sum(case when merchant_category  is null then 1 else 0 end ) as null_category,
sum(case when city               is null then 1 else 0 end ) as null_city,
sum(case when transaction_time   is null then 1 else 0 end ) as null_time,
sum(case when international_transaction  is null then 1 else 0 end ) as null_international_txn,
sum(case when card_present       is null then 1 else 0 end ) as null_card,
sum(case when failed_attempts     is null then 1 else 0 end ) as null_attempt,
sum(case when fraud              is null then 1 else 0 end ) as null_fraud
from transactions;

-- check for duplicate transaction ids
SELECT transaction_id, COUNT(*) AS cnt
FROM transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;

--  Distribution of Fraud vs Non-Fraud( % ) <<0 = Non-Fraud transaction, 1 = Fraud transaction>>

select 
fraud,count(*) as total_tnx,
round(count(*) *100.0/ sum(count(*)) over(),2 ) as percentage
from transactions
group by fraud
order by fraud;

-- ======================================
-- business queries (KPIs)
-- ====================================== 

-- kpi-1  total transactions , total amount , fraud rate 

select
count(*)  as total_tnx,
round(sum(transaction_amount)::NUMERIC,2 )  as total_amount,
sum(fraud)    as total_fraud_cases,
round(sum(fraud)*100.0/count(*),2)  as fraud_rate_perc,
round(sum(case when fraud=1 then transaction_amount else 0 end ):: NUMERIC,2) as total_fraud_amount
from transactions;

----  kpi -2 Fraud by Merchant Category
select 
    merchant_category,
    count(*)        as total_txns,
    sum(fraud)      as fraud_count,
    round(sum(fraud)*100.0/count(*), 2)    as fraud_rate_perc,
    round(sum(case when fraud=1 then transaction_amount else 0 end)::NUMERIC, 2) as fraud_amount                                                       
from transactions
group by merchant_category
order by fraud_rate_perc desc;

-- kpi -3 : Fraud by City
select
    city,
    count(*)    as total_txns,
    sum(fraud)  as fraud_count,
    round(sum(fraud)*100.0/count(*), 2)  as fraud_rate_perc
from transactions
group by  city
order by fraud_count desc;
 
 
-- kpi 4 : Fraud by Age Group
select 
    case
        when age between 18 and 29 then '18-29'
        when age between 30 and 39 then '30-39'
        when age between 40 and 49 then '40-49'
        when age between 50 and 59 then '50-59'
        else '60+'
    end         as age_group,
    count(*)    as total_txns,
    sum(fraud)  as fraud_count,
    round(sum(fraud)*100.0/count(*), 2) as fraud_rate_perc
from transactions
group by age_group
order by age_group;
 
 
-- kpi 5 : fraud by gender

select
    gender,
    count(*)     as total_txns,
    sum(fraud)   as fraud_count,
    round(sum(fraud) * 100.0 / count(*), 2) as fraud_rate_perc
from transactions
group by gender
order by fraud_count desc;


-- kpi 6 : fraud by transaction amount bucket

select
    case
        when transaction_amount < 500 then 'low (< 500)'
        when transaction_amount between 500 and 1999 then 'medium (500-1999)'
        when transaction_amount between 2000 and 3499 then 'high (2000-3499)'
        else 'very high (3500+)'
    end        as amount_bucket,
    count(*)   as total_txns,
    sum(fraud) as fraud_count,
    round(sum(fraud) * 100.0 / count(*), 2) as fraud_rate_perc
from transactions
group by amount_bucket
order by fraud_rate_perc desc;


-- kpi 7 : impact of failed attempts on fraud

select
    failed_attempts,
    count(*)                                 as total_txns,
    sum(fraud)                               as fraud_count,
    round(sum(fraud) * 100.0 / count(*), 2)  as fraud_rate_perc
from transactions
group by failed_attempts
order by failed_attempts;


-- kpi 8 : international vs domestic fraud

select
    case
        when international_transaction = 1
            then 'international'
        else 'domestic'
    end         as txn_type,
    count(*)    as total_txns,
    sum(fraud)  as fraud_count,
    round(sum(fraud) * 100.0 / count(*), 2)  as fraud_rate_perc
from transactions
group by txn_type;


-- kpi 9 : card present vs card not present fraud

select
    case
        when card_present = 1
            then 'card present'
        else 'card not present'
    end                           as card_type,
    count(*)                      as total_txns,
    sum(fraud)                    as fraud_count,
    round(sum(fraud) * 100.0 / count(*), 2)   as fraud_rate_perc
from transactions
group by card_type;


-- kpi 10 : hour-of-day fraud analysis
alter table transactions
alter column transaction_time
type timestamp
using to_timestamp(
    transaction_time,
    'dd-mm-yyyy hh24:mi'
);

select
    extract(hour from transaction_time) as hour_of_day,
    count(*)                            as total_txns,
    sum(fraud)                          as fraud_count,
    round( sum(fraud) * 100.0 / count(*), 2 )   as fraud_rate_perc
from transactions
group by hour_of_day
order by hour_of_day;


-- kpi 11 : top 10 high-risk merchants

select
    merchant_name,
    count(*)                                   as total_txns,
    sum(fraud)                                 as fraud_count,
    round(sum(fraud) * 100.0 / count(*), 2)    as fraud_rate_perc,
    round(sum(case when fraud = 1 then transaction_amount else 0 end )::numeric,2)                                                   as fraud_amount
from transactions
group by merchant_name
having count(*) > 1
order by fraud_rate_perc desc
limit 10;


-- ============================================================
-- create views for power bi
-- ============================================================

-- main clean view

create or replace view vw_transactions as

select

    transaction_id,
    cardholder_name,
    age,

    case
        when age between 18 and 29 then '18-29'
        when age between 30 and 39 then '30-39'
        when age between 40 and 49 then '40-49'
        when age between 50 and 59 then '50-59'
        else '60+'
    end as age_group,

    gender,
    transaction_amount,

    case
        when transaction_amount < 500 then 'low'
        when transaction_amount between 500 and 1999 then 'medium'
        when transaction_amount between 2000 and 3499 then 'high'
        else 'very high'
    end as amount_bucket,

    merchant_name,
    merchant_category,
    city,
    transaction_time,

    extract(hour from transaction_time)::integer
    as hour_of_day,

    case

        when extract(hour from transaction_time)
            between 0 and 5
            then 'late night'

        when extract(hour from transaction_time)
            between 6 and 11
            then 'morning'

        when extract(hour from transaction_time)
            between 12 and 17
            then 'afternoon'

        else 'evening'

    end as time_of_day,

    international_transaction,

    case
        when international_transaction = 1
            then 'international'
        else 'domestic'
    end as txn_type,

    card_present,

    case
        when card_present = 1
            then 'card present'
        else 'card not present'
    end as card_type,

    failed_attempts,
    fraud,

    case
        when fraud = 1
            then 'fraud'
        else 'legitimate'
    end as fraud_label

from transactions;


------------------------
-- kpi summary view for power bi cards
------------------------
create or replace view vw_kpi_summary as

select

    count(*) as total_transactions,

    round(
        sum(transaction_amount),
        2
    ) as total_amount,

    sum(fraud) as total_fraud_cases,

    round(
        sum(fraud) * 100.0 / count(*),
        2
    ) as fraud_rate_pct,

    round(
        avg(transaction_amount),
        2
    ) as avg_transaction_amount,

    round(
        sum(
            case
                when fraud = 1
                    then transaction_amount
                else 0
            end
        ),
        2
    ) as total_fraud_amount

from transactions;