import os
import pandas as pd
import pdfkit
import tqdm
from dotenv import load_dotenv

load_dotenv()

recipients = pd.read_sql('''
select distinct p.recipient_id,
    p.id as proposal_id,
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
''', con=os.getenv("DB_URL"), index_col='proposal_id')

proposals_to_report = pd.read_csv('reports/reports_to_check.csv')['proposal_id']

recipients = recipients[recipients.index.isin(proposals_to_report)]
recipients.loc[:, 'output_report'] = None
print("{:,.0f} recipients to create".format(len(recipients)))

for r in tqdm.tqdm(recipients.index):
    output_filename = "reports/beehive_legacy_{}.pdf".format(r)
    try:
        pdfkit.from_url(
            'http://127.0.0.1:3000/reports/{}'.format(r),
            output_filename,
            options={
                'quiet': '',
                'margin-left': '0',
                'margin-right': '0',
            },
        )
    except OSError:
        print("Could not create report", r)
    recipients.loc[r, 'output_report'] = output_filename
    recipients.sort_values("email").to_csv('reports/mailing_list.csv')
