<--- Lead to XQL --->
with xql_table as(
    select l.id                                             as lead_id,
           l.createddate                                    as lead_created,
           c.id,
           c.accountid,
           date(c.latest_mql_date__c)                       as contact_mql_date,
           /* Checks if MQL*/
           CASE
               WHEN c.latest_mql_date__c is not null and
                    c.isinvited__c is null and date(c.latest_mql_date__c) >= date(l.createddate)
                   THEN TRUE
               ELSE FALSE
               END                                          as mql_remql,
           /* Gets Latest XL */
           CASE
               WHEN c.latest_mql_date__c is null THEN date(c.pql_date__c)
               WHEN c.pql_date__c is null THEN date(c.latest_mql_date__c)
               WHEN date(c.latest_mql_date__c) >= date(c.pql_date__c) THEN date(c.latest_mql_date__c)
               ELSE date(c.pql_date__c)
               END                                          as Latest_XL_date,
           c.isinvited__c,
           /* Checks if PQL*/
           c.pql_type__c,
           date(c.pql_date__c)                              as pql_date,
           CASE
               WHEN date(c.pql_date__c) is not null and c.isinvited__c is null and
                    date(c.pql_date__c) >= date(l.createddate)
                   THEN TRUE
               ELSE FALSE
               END                                          as pql,
           /* Checks if routed to SDR */
           c.routed_to__c,
           CASE
               WHEN c.routed_to__c ilike '%SDR%' THEN 'routed_sdr'
               ELSE 'not_sdr'
               END                                          as sdr_bucket,
           CASE
               WHEN (c.latest_mql_date__c is not null and
                     c.isinvited__c is null and date(c.latest_mql_date__c) >= date(l.createddate)) or
                    (date(c.pql_date__c) is not null and c.isinvited__c is null and
                     date(c.pql_date__c) >= date(l.createddate)) THEN TRUE
               ELSE FALSE
               END                                          as mql_or_pql,
           /* Checks days between XL and Lead */
           date(c.latest_mql_date__c) - date(l.createddate) as day_lead_mql,
           date(c.pql_date__c) - date(l.createddate)        as day_lead_pql,
           CASE
               WHEN c.latest_mql_date__c is null THEN date(c.pql_date__c) - date(l.createddate)
               WHEN c.pql_date__c is null THEN date(c.latest_mql_date__c) - date(l.createddate)
               WHEN date(c.latest_mql_date__c) >= date(c.pql_date__c)
                   THEN date(c.latest_mql_date__c) - date(l.createddate)
               ELSE date(c.pql_date__c) - date(l.createddate)
               END                                          as day_lead_xl
    from sfdc_leads l
         join sfdc_contacts c on l.convertedcontactid = c.id
         join sfdc_accounts ac on l.convertedaccountid = ac.id
    where l.createddate >= '2020-02-01'
)
select l.id                                             as lead_id,
       l.convertedaccountid,
       date(l.createddate)                              as lead_createddate,
       1                                                as counter,
       l.name                                           as lead_name,
       l.email,
       l.company                                        as lead_company,
       CASE
           WHEN l.employees__c = 'Self-employed' THEN '1-SMB'
           WHEN l.employees__c = '1-10' THEN '1-SMB'
           WHEN l.employees__c = '11-50' THEN '1-SMB'
           WHEN l.employees__c = '51-100' THEN '1-SMB'
           WHEN l.employees__c = '51-200' THEN '2-COMM'
           WHEN l.employees__c = '101-200' THEN '2-COMM'
           WHEN l.employees__c = '201-300' THEN '2-COMM'
           WHEN l.employees__c = '201-500' THEN '3-MM'
           WHEN l.employees__c = '301-500' THEN '3-MM'
           WHEN l.employees__c = '501-1000' THEN '3-MM'
           WHEN l.employees__c = '1001-3000' THEN '3-MM'
           WHEN l.employees__c = '3001-5000' THEN '4-ENT'
           WHEN l.employees__c = '5001-10000' THEN '4-ENT'
           WHEN l.employees__c = '10001plus' THEN '4-ENT'
           WHEN l.employees__c = '10001+' THEN '4-ENT'
           WHEN l.employees__c = '10,001+' THEN '4-ENT'
           WHEN l.employees__c = '1001-5000' THEN '4-ENT'
           ELSE 'No Info'
           END                                          as company_segment,
       l.region__c,
       CASE
           WHEN l.region__c = 'USA' THEN 'NA'
           WHEN l.region__c = 'LATAM' THEN 'NA'
           WHEN l.region__c = 'ANZ' THEN 'NA'
           WHEN l.region__c = 'EMEA' THEN 'EMEA'
           WHEN l.region__c = 'APAC' THEN 'EMEA'
           ELSE 'Other'
           END                                          as region_bucket,
       l.country,
       l.converteddate,
       l.isconverted,
       l.bizible2__marketing_channel_lc__c,
       l.bizible2__ad_campaign_name_lc__c,
       l.bizible2__marketing_channel_path_lc__c,
       x.contact_mql_date,
       x.mql_remql,
       x.pql_date,
       x.Latest_XL_date,
       x.isinvited__c,
       x.pql_type__c,
       x.pql,
       x.routed_to__c,
       x.sdr_bucket,
       x.mql_or_pql,
       x.day_lead_mql,
       x.day_lead_pql,
       x.day_lead_xl,
       l.mk_customer_fit_segment__c
from sfdc_leads l
         left join xql_table x on l.id = x.lead_id and x.day_lead_xl <= 365  /* join XQL if within a year*/
where l.createddate >= '2020-02-01'
order by l.convertedaccountid, l.createddate, l.id;