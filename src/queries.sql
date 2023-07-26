[employers]
query1=SELECT employer_name, number_vacancies FROM employers

[vacancies]
query1=SELECT employers.employer_name, vacancy_name, salary_from, salary_to, vacancy_url FROM vacancies JOIN employers USING(employer_id)

[salary_avg]
query1=SELECT vacancy_name, ((salary_to + salary_from) / 2) AS salary_avg, vacancy_url FROM vacancies WHERE salary_from <> 0 AND salary_to <> 0

[salary_higher]
query1=SELECT vacancy_name, salary_from, salary_to, vacancy_url FROM vacancies WHERE (salary_from + salary_to) / 2 > (SELECT AVG((salary_from + salary_to) / 2) FROM vacancies WHERE salary_from <> 0 AND salary_to <> 0)

[keyword]
query1=SELECT vacancy_name, salary_from, salary_to, vacancy_url FROM vacancies WHERE LOWER(vacancy_name) LIKE keyword
