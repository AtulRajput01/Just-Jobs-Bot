import inspect
import json
import logging
import os
import re
import signal
import subprocess
import sys
import boto3
import uuid


from telegram import ChatAction, ParseMode, Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
)

"""
---Process ID Management Starts---
This part of the code helps out when you want to run your program in the background using '&'. This will
save the process id of the program going in the background in a file named 'pid'. Now, when you run your
program again, the last one will be terminated with the help of pid. If in case the no process exists
with the given process id, simply the pid file will be deleted and a new one with the current pid will be
created.
"""
currentPID = os.getpid()
if 'pid' not in os.listdir():
    with open('pid', mode='w') as f:
        print(str(currentPID), file=f)
else:
    with open('pid', mode='r') as f:
        try:
            os.kill(int(f.read()), signal.SIGTERM)
            logging.info(f'Terminating the previous instance of {os.path.realpath(_file_)}')
        except (ProcessLookupError, ValueError):
            subprocess.run(['rm', 'pid'])
    with open('pid', mode='w') as f:
        print(str(currentPID), file=f)
"""
---Process ID Management Ends---
"""

"""
---Token Management Starts---
This part will check for the config.json file which holds the Telegram and Channel ID and will also
give a user-friendly message if they are invalid. A new file is created if not present in the project
directory.
"""
configError = (
    'Please open config.json file located in the project directory and replace the value "0" of '
    'Telegram-Bot-Token with the Token you received from botfather.'
)
if 'config.json' not in os.listdir():
    with open('config.json', mode='w') as f:
        json.dump({'Telegram-Bot-Token': 0, 'Channel-Id': 0}, f)
        logging.info(configError)
        sys.exit(0)
else:
    with open('config.json', mode='r') as f:
        config = json.loads(f.read())
        if config['Telegram-Bot-Token']:
            logging.info('Token Present, continuing...')
            TelegramBotToken = config['Telegram-Bot-Token']
            if config['Channel-Id']:
                ChannelId = config['Channel-Id']
            else:
                logging.info((
                    'Channel ID is not present in config.json. Please follow the instruction on '
                    'README.md, run getid.py and replace the Channel ID you obtain.'
                ))
        else:
            logging.info(configError)
            sys.exit(0)
"""
---Token Management Ends---
"""

jobs_queue = {}
applicants_queue = {}

updater = Updater(token=TelegramBotToken)
dispatcher = updater.dispatcher


def start(update: Update, context: CallbackContext):
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    start_msg = inspect.cleandoc((
        'Hi there! To submit a job, use /submit\n'
        'To apply for a job, use /apply\n'
        'Use /help to get help'
    ))
    update.message.reply_text(start_msg)


def botHelp(update: Update, context: CallbackContext):
    help_msg = inspect.cleandoc((
        'Use /submit to submit a job.\n'
        'After your submission, the job will be displayed on @cuedjobs channel.\n\n'
        'Use /apply to apply for a job. You will be asked to provide your details, including a profile picture, '
        'name, age, highest qualification, skills, experience, and the role you are looking for.\n\n'
        'To report a bug or contribute to this bot, visit '
        'https://github.com/AtulRajput01/Just-Jobs-Bot'
    ))
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    context.bot.send_message(
        chat_id=update.message.chat_id, parse_mode=ParseMode.MARKDOWN, text=help_msg,
    )


# AWS credentials
aws_access_key_id = "AKIA4SCY35W54RDN5UMM"
aws_secret_access_key = "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"
aws_region = "us-east-1"

# DynamoDB table name
dynamodb_table_name = "cued_bot2"

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name=aws_region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
table = dynamodb.Table(dynamodb_table_name)


def submitJob(update: Update, context: CallbackContext):
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    jobs_queue[update.message.chat_id] = []
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='After submission, the job will be displayed on @cuedjobs channel.',
    )
    context.bot.send_message(chat_id=update.message.chat_id, text='What is your company name?')


def addDetails(update: Update, context: CallbackContext):
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    if update.message is not None and update.message.chat_id in jobs_queue:
        if len(jobs_queue[update.message.chat_id]) == 11:
            jobs_queue[update.message.chat_id].append(update.message.text)
            context.bot.send_message(
                chat_id=update.message.chat_id, text='What is your job designation?',
            )
        elif len(jobs_queue[update.message.chat_id]) == 1:
            jobs_queue[update.message.chat_id].append(update.message.text)
            context.bot.send_message(
                chat_id=update.message.chat_id, text='What is your job description?',
            )
        elif len(jobs_queue[update.message.chat_id]) == 2:
            jobs_queue[update.message.chat_id].append(update.message.text)
            context.bot.send_message(
                chat_id=update.message.chat_id, text='What are the qualifications needed?',
            )
        elif len(jobs_queue[update.message.chat_id]) == 3:
            jobs_queue[update.message.chat_id].append(update.message.text)
            context.bot.send_message(
                chat_id=update.message.chat_id, text='What is the experience needed?',
            )
        elif len(jobs_queue[update.message.chat_id]) == 4:
            jobs_queue[update.message.chat_id].append(update.message.text)
            context.bot.send_message(
                chat_id=update.message.chat_id, text='What is the joining date?',
            )
        elif len(jobs_queue[update.message.chat_id]) == 5:
            jobs_queue[update.message.chat_id].append(update.message.text)
            context.bot.send_message(
                chat_id=update.message.chat_id, text='What is the last date to apply?',
            )
        elif len(jobs_queue[update.message.chat_id]) == 6:
            jobs_queue[update.message.chat_id].append(update.message.text)
            context.bot.send_message(
                chat_id=update.message.chat_id, text='What is the salary offered?',
            )
        elif len(jobs_queue[update.message.chat_id]) == 7:
            jobs_queue[update.message.chat_id].append(update.message.text)
            context.bot.send_message(
                chat_id=update.message.chat_id, text='Who is the contact person?',
            )
        elif len(jobs_queue[update.message.chat_id]) == 8:
            jobs_queue[update.message.chat_id].append(update.message.text)
            context.bot.send_message(chat_id=update.message.chat_id, text='What is your email id?')
        elif len(jobs_queue[update.message.chat_id]) == 9:
            if re.fullmatch(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', update.message.text,
            ):
                jobs_queue[update.message.chat_id].append(update.message.text)
                context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text='What is your phone number? (reply "skip" to skip this question)',
                )
            else:
                context.bot.send_message(
                    chat_id=update.message.chat_id, text='Please enter a valid email address.',
                )
        elif len(jobs_queue[update.message.chat_id]) == 10:
            PHONE_NO_REGEX = (
                r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??'
                r'\d{4})'
            )
            if re.fullmatch(
                PHONE_NO_REGEX,
                update.message.text,
            ):
                jobs_queue[update.message.chat_id].append(update.message.text)

                # Construct the message with job details
                phone_number = jobs_queue[update.message.chat_id][10] if len(
                    jobs_queue[update.message.chat_id]) == 11 else '(not submitted)'
                tg_job_msg = inspect.cleandoc((
                    f'Company Name: {jobs_queue[update.message.chat_id][0]}\n'
                    f'Job Description: {jobs_queue[update.message.chat_id][2]}\n'
                    f'Job Designation: {jobs_queue[update.message.chat_id][1]}\n'
                    f'Qualification Needed: {jobs_queue[update.message.chat_id][3]}\n'
                    f'Experience Needed: {jobs_queue[update.message.chat_id][4]}\n'
                    f'Joining Date: {jobs_queue[update.message.chat_id][5]}\n'
                    f'Last Date to Connect: {jobs_queue[update.message.chat_id][6]}\n'
                    f'Salary Offered: {jobs_queue[update.message.chat_id][7]}\n'
                    f'Contact Person: {jobs_queue[update.message.chat_id][8]}\n'
                    f'Email Id: {jobs_queue[update.message.chat_id][9]}\n'
                    f'Phone No: {phone_number}'
                ))

                # Send the job details to the specified channel
                context.bot.send_message(
                    chat_id=ChannelId, text=tg_job_msg, parse_mode=ParseMode.MARKDOWN)

                # Add to DynamoDB for recruiters
                recruiter_id = str(update.message.from_user.id)
                user_id = str(update.message.from_user.id)
                job_details = {
                    'recruiter_id': recruiter_id,
                    'user_id': user_id,
                    'Company Name': jobs_queue[update.message.chat_id][0],
                    'Job Designation': jobs_queue[update.message.chat_id][1],
                    'Job Description': jobs_queue[update.message.chat_id][2],
                    'Qualifications Needed': jobs_queue[update.message.chat_id][3],
                    'Experience Needed': jobs_queue[update.message.chat_id][4],
                    'Joining Date': jobs_queue[update.message.chat_id][5],
                    'Last Date to Apply': jobs_queue[update.message.chat_id][6],
                    'Salary Offered': jobs_queue[update.message.chat_id][7],
                    'Contact Person': jobs_queue[update.message.chat_id][8],
                    'Email Id': jobs_queue[update.message.chat_id][9],
                    'Phone No': jobs_queue[update.message.chat_id][10],
                }
                recruiter_table.put_item(Item=job_details)

                # Clear the jobs_queue for the next submission
                del jobs_queue[update.message.chat_id]

                # Notify the user
                context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text='Thank you. Your Job has been posted to @cuedjobs',
                )
    elif update.message.chat.type == 'private':
        context.bot.send_message(
            chat_id=update.message.chat_id, text='Please use /submit to submit jobs.',
        )

# Other imports and setup code...

# AWS credentials
aws_access_key_id = "AKIA4SCY35W54RDN5UMM"
aws_secret_access_key = "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"
aws_region = "us-east-1"

# DynamoDB table name
dynamodb_table_name = "cued_bot"

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name=aws_region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
table = dynamodb.Table(dynamodb_table_name)


def apply(update: Update, context: CallbackContext):
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    applicants_queue[update.message.chat_id] = {'answers': [], 'resume_link': ''}
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='After submission, your details will be reviewed by recruiters. Use /help for more info.',
    )
    context.bot.send_message(chat_id=update.message.chat_id, text='What is your full name?')


def addApplicantDetails(update: Update, context: CallbackContext):
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    if update.message is not None and update.message.chat_id in applicants_queue:
        current_step = len(applicants_queue[update.message.chat_id]['answers'])

        if current_step == 0:
            applicants_queue[update.message.chat_id]['answers'].append(update.message.text)
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text='What is your age?',
            )
        elif current_step == 1:
            applicants_queue[update.message.chat_id]['answers'].append(update.message.text)
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text='What is your highest qualification?',
            )
        elif current_step == 2:
            applicants_queue[update.message.chat_id]['answers'].append(update.message.text)
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text='What skills do you possess?',
            )
        elif current_step == 3:
            applicants_queue[update.message.chat_id]['answers'].append(update.message.text)
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text='What is your relevant work experience? (mention role and duration)',
            )
        elif current_step == 4:
            applicants_queue[update.message.chat_id]['answers'].append(update.message.text)
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text='Provide a link to your resume/cv on Google Drive or any other cloud storage (e.g., Dropbox).'
            )
        elif current_step == 5:
            applicants_queue[update.message.chat_id]['answers'].append(update.message.text)
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text='Provide a link to your LinkedIn profile.'
            )
        elif current_step == 6:
            linkedin_profile = update.message.text
            applicants_queue[update.message.chat_id]['answers'].append(linkedin_profile)

            # Process the gathered information
            full_name = applicants_queue[update.message.chat_id]['answers'][0]
            age = applicants_queue[update.message.chat_id]['answers'][1]
            highest_qualification = applicants_queue[update.message.chat_id]['answers'][2]
            skills = applicants_queue[update.message.chat_id]['answers'][3]
            experience = applicants_queue[update.message.chat_id]['answers'][4]
            resume_link = applicants_queue[update.message.chat_id]['answers'][5]
            linkedin_profile = applicants_queue[update.message.chat_id]['answers'][6]

            # Save user data to DynamoDB
            user_details = {
                'telegram_user_id': str(update.message.from_user.id),
                'user_id': str(update.message.from_user.id),
                'Full Name': full_name,
                'Age': age,
                'Highest Qualification': highest_qualification,
                'Skills': skills,
                'Experience': experience,
                'Resume Link': resume_link,
                'LinkedIn Profile': linkedin_profile,
            }
            table.put_item(Item=user_details)

            tg_applicant_msg = inspect.cleandoc(f"""
                Applicant Information:
                Name: {full_name}
                Age: {age}
                Highest Qualification: {highest_qualification}
                Skills: {skills}
                Experience: {experience}
                Resume Link: [Click Here]({resume_link})
                LinkedIn Profile: [Click Here]({linkedin_profile})
            """)

            context.bot.send_message(
                chat_id=ChannelId, text=tg_applicant_msg, parse_mode=ParseMode.MARKDOWN
            )
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text='Thank you. Your application has been submitted. Recruiters will review your details.',
            )
            # Clear the applicant queue for the next submission
            del applicants_queue[update.message.chat_id]

    elif update.message.chat.type == 'private':
        context.bot.send_message(
            chat_id=update.message.chat_id, text='Please use /apply to submit job applications.',
        )

# Other code...

dispatcher.add_handler(CommandHandler('apply', apply))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, addApplicantDetails))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, addDetails))


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', botHelp))
dispatcher.add_handler(CommandHandler('submit', submitJob))
dispatcher.add_handler(MessageHandler(Filters.text, addDetails))


updater.start_polling()
