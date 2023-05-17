use freshdesk;

select
	tx.id,
    cn.name,
    cm.name,
    tm.time_spent,
    cm.custom_fields->>'$.customerid' AS customerid,
    tx.subject
   
from time_entries as tm
	left join tickets as tx on tm.ticket_id = tx.id
	left join companies as cm on tx.company_id = cm.id
	left join contacts as cn on tx.requester_id = cn.id
where tm.billable = 1

order by cm.name, tx.id

