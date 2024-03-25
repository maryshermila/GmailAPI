RULES = {
    "rules": [
      {
        "name": "Rule 1",
        "type": "all",
        "conditions": [
          {
            "field": "from_address",
            "operator": "contains",
            "value": "jobalerts-noreply@linkedin.com"
          },
          {
            "field": "subject",
            "operator": "contains",
            "value": "Hiring now"
          },
          {
            "field": "date",
            "operator": "less_than",
            "value": "2 days"
          }
        ],
        "actions": [
          {
            "action": "move_to_mailbox",
            "mailbox": "Inbox"
          },
          {
            "action": "mark_as_read"
          }
        ]
      }
    ]
}
  