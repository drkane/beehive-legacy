from flask import Flask, render_template
import pandas as pd
import os
import base64
import datetime


from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

db_con = os.environ.get('DB_URL')

proposals = pd.read_pickle('proposals.pkl')
recipients = pd.read_sql('select * from recipients', con=db_con, index_col='id')
themes = pd.read_pickle('themes.pkl')
funds = pd.read_sql('''
select a.proposal_id,
	replace(
		case when f."name" = 'Main Grants' or f."name" is null
		then f2."name"
		else concat( f2."name", ' - ', f."name" ) end,
		'Big Lottery Fund',
		'National Lottery Community Fund') as funder,
	coalesce(f.website, f2.website) as fund_website
from assessments a 
	inner join funds f 
		on a.fund_id = f.id
	inner join funders f2 
		on f.funder_id = f2.id
where a.suitability_status = 'approach'
''', con=db_con)

@app.route('/report/<int:r_id>')
def generate_report(r_id):
    r = recipients[recipients.index==r_id].iloc[0]
    ps = proposals[proposals.recipient_id==r_id].reset_index().to_dict(orient='records')
    for p in ps:
        p['themes'] = themes.loc[themes.proposal_id==p['id'], 'parent_name'].to_list()
        p['funds'] = funds.loc[funds.proposal_id==p['id']].to_dict(orient='records')
    return render_template(
        'report_template.html.j2',
        recipient=r.to_dict(),
        proposals=ps,
        now=datetime.datetime.now().date(),
    )
