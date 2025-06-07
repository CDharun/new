import boto3
import json
import pandas as pd
import io
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter

# Define the S3 bucket and file details
s3_bucket = "agent-generic-response"
s3_key = "input-file/19may.csv"
# Initialize S3 client
s3 = boto3.client('s3')
s3_data = s3.get_object(Bucket=s3_bucket, Key=s3_key)
contents = pd.read_csv(io.BytesIO(s3_data['Body'].read()))
# Print the initial dataframe
print("Initial DataFrame:")
print(contents)
prompt_template = """
You are tasked with converting a customer service agent's response into a **generic, reusable knowledgebase article-style answer**.

Instructions:
- Create a more **neutral, bot-appropriate** version that does **not** imply the bot is taking action beyond offering guidance. 


Example response:
- "The Resolutions team may attempt to reach out with an outcome after reviewing the claim. For further assistance and clarification, please contact our customer service at 929-242-0556 before 9 PM EST to be transferred to an account manager from the Resolutions department."
- "You have two options: you can hire your own licensed and insured technician to assess the issue and provide us with a diagnostic report for review, which we can use to determine the outcome (this is called a reimbursement claim), or you can file the claim with us, and we will find a technician, arrange the appointment, and follow the same review process. In both cases, you will need to file the claim first."
- "Thanks for letting us know!Since there's no option to log the technician's arrival directly here,please contact our chat general customer service agent by typing " Agent " in this chat .Our agents are available to assist you with update this information right away."
- "Please contact our general customer service agent by typing 'Agent' in the chat to update or get your claim details. Our agents are available to assist you with any necessary updates and provide further support as needed."
- "Sorry for the inconvenience,I'm sorry to hear you've decided to cancel your policy. "Please contact our customer service team by typing 'Agent' in the chat or at  929-242-0556, who will provide you with the cancellation request form. Kindly fill it out, and one of our account managers will follow up with you to finalize the cancellation and process your prorated refund."
- "Thank you for following up! Diagnosis report provided by the technician will be reviewed by our Resolutions Department. Once the review is complete, an account manager will reach out to you regarding the next steps.
- If you'd like immediate confirmation or an update on your claim status, please contact our General Customer Service Department by typing "Agent" in the chat.Our agents are available to assist you further."
- "Once a claim is placed, it will take 1–2 business days to assign a technician. They will then get in contact with you, or you will receive an email notification of the appointment day. We will receive a diagnosis from the technician for reviewing your issues and coverages. The review team will call you to provide you with the outcome of the claim and how to solve the problem that you are having."

**Important Rules:**  
**No Escalation Promises by the Bot**  
- The bot should **not** say it will escalate the case.  
- Instead, instruct customers to **contact the relevant department** mentioned by the agent.  
- Example: "If further assistance is needed, please contact our [Department Name] for support."  
- Avoid: "We will escalate your case to [Department Name]."  

**NO Customer-Specific Details in the Response** 
- Strictly remove any information that is specific to an individual customer.
- Absolutely NO customer- or case-specific data.
- Prohibited details include:
    - Card numbers (e.g., "card ending in 7956")    
    - Payment amounts (e.g., "$57.50")
    - Claim IDs, invoice numbers, transaction IDs
    - Customer names, email addresses, phone numbers
    - Technician names or any identifiable third-party information
    - **Appliance or product brand names (e.g., Samsung, GE, Whirlpool)**
    - **Credit card numbers, expiration dates, or any payment details**
    - **Specific calendar dates (e.g., "May 22", "April 15", "next Tuesday")**
    - Replace specific dates with generic equivalents when necessary.
- Instead, provide a generic explanation of the process.
-Example Structure:  
- **Original**: "Kindly confirm the card ending in 7956 is the one you are trying to use for the payment of $57.50."  
- **Improved**: "Please confirm if the payment method on file is the one you wish to use for the transaction."
- **Rationale**: Avoids disclosing specific payment details, reducing privacy risks.  

**No Pricing or Plan Amounts**  
- Do **not** mention any dollar values or subscription costs.  
- Instead, refer the customer to the **Sales Department** for plan or pricing details.

**No Technician or Vendor Identifying Information**
- Strictly prohibited:
  - Technician or vendor names (e.g., "ECO DRAINS AND PLUMBING LLC")
  - Phone numbers (e.g., (443) 929-8179)
  - Email addresses (e.g., collins@...)
  - Any company-specific or personal contact information of third-party service providers
- Instead, use generalized phrasing like:
  - "Please contact the technician or company that completed the service."
  - "The service provider who completed the repair may be able to provide this information."
> **Violation of this rule makes the response unusable.Do not include any technician or vendor names or contact information in any case.**

**Department Contact Instructions:**

Only provide department phone numbers in the following specific situations:
1. **Live discussion regarding the Resolution outcome**  
2. **Live sourcing for unit replacements**  
3. **Live payment (credit card/bank info)**  
4. **Live Retention of Pending Cancellation Policies**  

For these cases, include the appropriate phone number from the list below.

All other department references should instruct the user to contact the department **by typing "Agent" in the chat**.

Department Phone Number Reference:
- **Customer Service Department:** 929-242-0556
- **Billing Department:** 929-463-9603
- **Sales Department:** 866-225-7958
- **Dispatch Department:** 929-463-9331
- **Authorization Department:** 929-463-9331 


Customer Inquiry:
{question}

Agent's Combined Response:
{agent_response}

### Output Format:  
Return only the **reworded, chatbot-appropriate response** as 1–2 short paragraphs.  
Make sure it is **clear, neutral**, and easy for a customer to read. 
**Avoid repeating the same point or phrasing. Say it once clearly and move on.**
Ensure it follows the tone and structure of the examples above.  
Do **not** include introductions, summaries, or agent/bot names.
“Prohibited: All exact dates, weekdays, months, or calendar years. Use only vague timing such as ‘soon’, ‘within a few days’, or ‘recently’. Any output violating this is unusable.”
"Rephrase all content to be applicable to any customer in any situation, without personalization."
"If the original response includes customer-specific content, generalize it into standard process descriptions."
"""

# Initialize Bedrock client
bedrock = boto3.client("bedrock-runtime")

def get_generic_response(question, agent_response):
    formatted_prompt = prompt_template.format(question=summarized_question, agent_response=agent_response)
    # payload = {
    #     "prompt": f"\n\nHuman: {formatted_prompt} \n\nAssistant: ",
    #     "max_tokens_to_sample": 500,
    #     "temperature": 0.3,
    #     "top_k": 250,
    #     "top_p": 0.95
    # }   
    # body = json.dumps(payload)
    # model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    # response = bedrock.invoke_model(
    #     body=body,
    #     modelId=model_id,
    #     accept="application/json",
    #     contentType="application/json"
    # )
    # response_body = json.loads(response['body'].read())
    # return response_body.get("completion", "No response generated")
    
        # Format the request payload using the model's native structure.
    native_request = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens":350,
    "temperature": 0.5,
    "top_k": 50,
    "top_p": 0.85,
    "messages": [
        {
            "role": "user",
            "content": [{"type": "text", "text": formatted_prompt}],
        }
    ],
}

    # Convert the native request to JSON.
    request = json.dumps(native_request)
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    try:
        # Invoke Mistral model
        response = bedrock.invoke_model(modelId=model_id, body=request)

        # Parse model response
        response_body = json.loads(response["body"].read())
        response_text = response_body["content"][0]["text"]

        return response_text.strip()

    except Exception as e:
        return f"Error: {str(e)}"

# Function to extract and combine all customer messages into a single meaningful question
def get_customer_question(conversation):
    customer_rows = conversation[conversation['ParticipantRole'].str.lower() == 'customer']
    if not customer_rows.empty:
        combined_question = " ".join(customer_rows['Content'].dropna().tolist())
        return combined_question.strip()
    return "No customer question found"
# Function to extract all agent responses and combine meaningfully
def get_agent_response(conversation):
    agent_rows = conversation[conversation['ParticipantRole'].str.lower() == 'agent']
    if not agent_rows.empty:
        combined_response = ' '.join(agent_rows['Content'].tolist())
        return combined_response
    return "No agent response found"

def summarize_customer_question(raw_customer_text):

    summary_prompt = f"""
You are an AI assistant tasked with extracting a customer's intent from their message and converting it into a **generic, reusable conditional sentence** that starts with: **"If a customer..."**

### Instructions:
1. Generalize the customer's inquiry or complaint by removing specific appliance names (e.g., refrigerator, dishwasher), brand names (e.g., LG), part names, and specific symptoms.
2. Write only a **neutral, reusable condition statement** for a chatbot (not a response), in the following format:
   "If a customer [summary of the situation or intent],"
3. Ensure the condition applies to any appliance or service request — not just the specific one mentioned.
4. Do not include device names, brand names, or location-specific details.
5. Do **not** include the word "Instruction:" or any response text after the condition.

### Few-shot Examples:
If a customer requests to cancel their service contract and asks about getting a prorated refund.  
If a customer is unable to file a new claim due to having an existing open claim.  
If a customer needs to file a new claim for an issue with their appliance and inquires about the claims process, coverage, and policy details.  
If a customer requests to reschedule a technician visit due to an unresolved appliance issue.

### Customer Message:
{raw_customer_text}
"""

    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens":500,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": summary_prompt}],
            }
        ],
    }
    # Convert the native request to JSON.
    request = json.dumps(native_request)
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    try:
        # Invoke Mistral model
        response = bedrock.invoke_model(modelId=model_id, body=request)

        # Parse model response
        response_body = json.loads(response["body"].read())
        response_text = response_body["content"][0]["text"]

        return response_text.strip()

    except Exception as e:
        return f"Error: {str(e)}"

    # payload = {
    #     "prompt": f"\n\nHuman: {summary_prompt}\n\nAssistant: ",
    #     "max_tokens_to_sample": 400,
    #     "temperature": 0.3,
    #     "top_k": 250,
    #     "top_p": 0.95
    # }
    # body = json.dumps(payload)
    # response = bedrock.invoke_model(
    #     body=body,
    #     modelId="anthropic.claude-v2",
    #     accept="application/json",
    #     contentType="application/json"
    # )
    # response_body = json.loads(response['body'].read())
    # return response_body.get("completion", raw_customer_text)

# Group conversations by initialcontactid
grouped_conversations = contents.groupby('initialcontactid')
# Process each conversation and store results
results = []
for contact_id, group in grouped_conversations:
    roles = set(group['ParticipantRole'].str.lower())
    if 'agent' not in roles:
        print(f"\nSkipping InitialContactId: {contact_id} (No agent messages)")
        continue
    # # Check if there's at least one customer or agent message
    # has_customer = any(group['ParticipantRole'].str.lower() == 'customer')
    # has_agent = any(group['ParticipantRole'].str.lower() == 'agent')
    # # Skip empty conversations
    # if not has_customer and not has_agent:
    #     print(f"\nSkipping InitialContactId: {contact_id} (No customer/agent messages)")
    #     continue
    print(f"\nProcessing InitialContactId: {contact_id}")
    # Get combined raw messages from the customer
    raw_question = get_customer_question(group)
    # Skip if customer message is empty or just whitespace
    if not raw_question.strip() or raw_question.strip().lower() == "no customer question found":
        print(f"Skipping InitialContactId: {contact_id} (No meaningful customer question)")
        continue
    summarized_question = summarize_customer_question(raw_question)
    print(f"Customer Question: {summarized_question}")
    agent_response = get_agent_response(group)
    generic_response = get_generic_response(summarized_question, agent_response)
    print(f"Generic Response: {generic_response}")
    results.append({
        'InitialContactId': contact_id,
        'CustomerQuestion': summarized_question,
        # 'AgentResponse': agent_response,
        'GenericResponse': generic_response
    })
# Convert results to DataFrame
results_df = pd.DataFrame(results)
# Extract base name (like '12MAR') from input file key
input_filename = s3_key.split('/')[-1]  # "12MAR.csv"
base_name = input_filename.replace('.csv', '')  # "12MAR"

# # Save results to CSV
from datetime import datetime

# Get today's date
today = datetime.today()
year = today.year
month = today.month
day = today.day

# Generate a filename, e.g., file-26.csv or something dynamic
output_filename = f"file-{day}.csv"

# Define the partitioned S3 key using current date
output_key = f"model-output/year={year}/month={month}/day={day}/{output_filename}"

# Save results to CSV in memory buffer
output_buffer = io.StringIO()
results_df.to_csv(output_buffer, index=False)

# Upload result to S3
s3.put_object(
    Bucket=s3_bucket,
    Key=output_key,
    Body=output_buffer.getvalue()
)

print("\nResults have been saved to S3 at:", f"s3://{s3_bucket}/{output_key}")


# # Create Excel file in-memory
# output_excel = io.BytesIO()

# # Write dataframe to Excel file using openpyxl engine
# with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
#     results_df.to_excel(writer, index=False, sheet_name='AgentResponses')

#     # Access the workbook and worksheet
#     workbook = writer.book
#     worksheet = writer.sheets['AgentResponses']

#     # Set wrap text and auto-adjust column width
#     for col_idx, column_cells in enumerate(worksheet.columns, start=1):
#         max_length = 0
#         for cell in column_cells:
#             cell.alignment = Alignment(wrap_text=True)
#             if cell.value:
#                 max_length = max(max_length, len(str(cell.value)))
#         adjusted_width = min(max_length + 5, 100)
#         worksheet.column_dimensions[get_column_letter(col_idx)].width = adjusted_width

# Upload Excel file to S3
# output_excel.seek(0)  # Reset pointer to beginning
# output_key_excel = f"output-file/{base_name}-agent-generic-response.xlsx"

# s3.put_object(
#     Bucket=s3_bucket,
#     Key=output_key_excel,
#     Body=output_excel.getvalue(),
#     ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
# )

# print("\nFormatted Excel file with wrapped text has been saved to S3 at:", f"s3://{s3_bucket}/{output_key_excel}")




