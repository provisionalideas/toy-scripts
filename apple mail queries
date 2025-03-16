-- the following queries are for Apple Mail; you can find the database in ~/Mail/V8 [or whatever is latest version]/Envelope Index

-- this one counts the number of emails from each sender; useful for making big dents in your inbox quickly
select messages.sender, addresses.address, addresses.comment, count(*) as counter from messages
left join addresses on messages.sender=addresses.ROWID
left join mailboxes on messages.mailbox=mailboxes.ROWID
where mailboxes.url like '%INBOX%' or url like '%Inbox%' or url like '%inbox%' or url like '%All%20Mail%'
group by sender
order by counter asc;

-- total inbound emails per month
select count(*) from messages
left join addresses as senderName on messages.sender=senderName.ROWID
left join recipients on messages.ROWID=recipients.message_id
left join addresses as recipientName on recipients.address_id=recipientName.ROWID
left join mailboxes on messages.mailbox=mailboxes.ROWID
where senderName.address not like '%YOUR EMAIL HERE%'
and recipientName.address like '%YOUR EMAIL HERE%'
and date_sent > strftime('%s',date('now','start of month','-12 month'));

-- get total inbound emails month-month
select strftime('%m-%Y',datetime(messages.date_sent,'unixepoch')) as month, count(*) from messages
left join addresses as senderName on messages.sender=senderName.ROWID
left join recipients on messages.ROWID=recipients.message_id
left join addresses as recipientName on recipients.address_id=recipientName.ROWID
left join mailboxes on messages.mailbox=mailboxes.ROWID
where senderName.address not like '%YOUR EMAIL HERE%'
and recipientName.address like '%YOUR EMAIL HERE%'
group by month
order by date_sent asc;

-- get total outbound emails month-month
select strftime('%m-%Y',datetime(messages.date_sent,'unixepoch')) as month, count(*) from messages
left join addresses as senderName on messages.sender=senderName.ROWID
left join recipients on messages.ROWID=recipients.message_id
left join addresses as recipientName on recipients.address_id=recipientName.ROWID
left join mailboxes on messages.mailbox=mailboxes.ROWID
where senderName.address like '%YOUR EMAIL HERE'
and recipientName.address not like '%YOUR EMAIL HERE%'
group by month
order by date_sent asc;

// get total outbound to specific addresses month-month

select strftime('%m-%Y',datetime(messages.date_sent,'unixepoch')) as month, count(*) from messages
left join addresses as senderName on messages.sender=senderName.ROWID
left join recipients on messages.ROWID=recipients.message_id
left join addresses as recipientName on recipients.address_id=recipientName.ROWID
left join mailboxes on messages.mailbox=mailboxes.ROWID
where senderName.address like '%YOUR EMAIL HERE%'
and recipientName.address not like '%sYOUR EMAIL HERE%'
and recipientName.address like '%TARGET EMAIL HERE%'
group by month
order by date_sent asc;
