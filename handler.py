def lambda_handler(event, context):
    http_method = event.get('httpMethod')
    path = event.get('path', '')

    if http_method == 'GET' and path == '/events':
        return get_events()
    elif http_method == 'POST' and path == '/events':
        return add_event(event)
    elif http_method == 'POST' and '/join' in path:
        return join_event(event)
    else:
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Method Not Allowed'})
        }

def join_event(event):
    """Add a user to the event's attendee list."""
    try:
        body = json.loads(event['body'])
        event_id = event['pathParameters']['event_id']  # Extract event ID from path

        if not all(k in body for k in ('name', 'email', 'contact')):
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing required fields'}),
            }

        # Update the event to include the attendee
        table.update_item(
            Key={'id': event_id},
            UpdateExpression="SET attendees = list_append(if_not_exists(attendees, :empty_list), :new_attendee)",
            ExpressionAttributeValues={
                ':empty_list': [],
                ':new_attendee': [{
                    'name': body['name'],
                    'email': body['email'],
                    'contact': body['contact']
                }]
            },
            ReturnValues="UPDATED_NEW"
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Successfully joined the event'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error joining event', 'error': str(e)})
        }
