[employers]
query1=SELECT employer_name, number_vacancies FROM employers

[vacancies]
query1=SELECT employers.employer_name, vacancy_name, salary_from, salary_to, vacancy_url FROM vacancies JOIN employers USING(employer_id)
