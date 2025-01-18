from openai import OpenAI

def summarize_emails(emails):
    summaries = []
    client = OpenAI()
    # OpenAI.api_key = os.getenv('OPENAI_API_KEY')
    
    for email in emails:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Use a valid model
            messages=[
                {"role": "system", "content": "You are an email summarizer. You will be given an email and you will summarize it into a single sentence."},
                {"role": "user", 
                 "content": email.body}
            ]
        )
        # Extract the summary text from the message object
        message = completion.choices[0].message
        summary_text = ''

        if isinstance(message.content, list):
            # Handle the case where content is a list
            for content_piece in message.content:
                if content_piece['type'] == 'text':
                    summary_text += content_piece['text']['value']
        else:
            # Handle the case where content is a string
            summary_text = message.content

        summaries.append({
            'email_id': email.id,
            'summary': summary_text.strip()
        })

    return summaries