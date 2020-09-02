import os
import pandas as pd
import pdfkit
import tqdm
from dotenv import load_dotenv

load_dotenv()

recipients = pd.read_sql('''
select distinct p.recipient_id,
    r.name as "recipient_name",
    u.first_name,
    u.last_name,
    u.email,
    u.last_seen,
    u.agree_to_terms 
from proposals p 
    inner join recipients r 
        on p.recipient_id = r.id 
    inner join users u
        on p.user_id = u.id
''', con=os.getenv("DB_URL"), index_col='recipient_id')
print("{:,.0f} recipients to create".format(len(recipients)))

recipients = recipients.sample(10)
recipients.loc[:, 'output_report'] = None

for r in tqdm.tqdm(recipients.index):
    output_filename = "reports/beehive_legacy_{}.pdf".format(r)
    pdfkit.from_url(
        'http://127.0.0.1:5000/report/{}'.format(r),
        output_filename,
        options={ 'quiet': '' },
    )
    recipients.loc[r, 'output_report'] = output_filename

recipients.to_csv('reports/mailing_list.csv')