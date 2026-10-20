-- 08-technology-jobs — comp analytics in SQL.
-- Loads: data/processed/salaries.csv -> `salaries` (work_year, job_title, experience_level,
--        remote_ratio, remote_label, company_location, salary_usd).

-- Median pay ladder by geography (records>=30 honesty filter)
SELECT company_location, COUNT(*) AS records,
       APPROX_QUANTILES(salary_usd, 100)[OFFSET(50)] AS median_salary_usd   -- BigQuery
FROM salaries GROUP BY company_location HAVING COUNT(*) >= 30
ORDER BY median_salary_usd DESC;

-- Leveling premium: SE vs EN medians
SELECT experience_level, COUNT(*) AS records,
       APPROX_QUANTILES(salary_usd, 100)[OFFSET(50)] AS median_salary_usd
FROM salaries GROUP BY experience_level ORDER BY median_salary_usd DESC;

-- Work-mode menu: remote vs hybrid vs onsite
SELECT remote_label, COUNT(*) AS records,
       APPROX_QUANTILES(salary_usd, 100)[OFFSET(50)] AS median_salary_usd
FROM salaries GROUP BY remote_label ORDER BY median_salary_usd DESC;

-- Top roles (n>=10)
SELECT job_title, COUNT(*) AS records,
       APPROX_QUANTILES(salary_usd, 100)[OFFSET(50)] AS median_salary_usd
FROM salaries GROUP BY job_title HAVING COUNT(*) >= 10
ORDER BY median_salary_usd DESC LIMIT 15;
