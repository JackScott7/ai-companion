import argparse
from companion import JarvisCompanion


def main():
    jarvis = JarvisCompanion(args.verbose, args.save_chat, args.context)

    if args.list_chats:
        [print(x) for x in jarvis.get_all_chats]
        exit(0)

    status = jarvis.is_llm_online(args.verbose)
    if not status:
        exit(1)
    try:
        jai_response = jarvis.llm_generate(args.prompt)
        jarvis.stream_llm_response(jai_response, True if not args.markdown else False)
    except KeyboardInterrupt:
        exit(1)

if __name__ == '__main__':
    # TODO make LLM's customizable (config in a json file, jarvis_config.json): ✅
    # TODO implement --save-chat
    parser = argparse.ArgumentParser(
        "Ask questions, and you shall receive answers",
        description="An AI Based on meta's Llama for asking questions and giving short answers "
                    "until deleted manually, typically every call to the jarvis.py is a new conversation "
                    "a basic usage is: prompt the jarvis.py with --save-chat to save every chat from that point on "
                    "all saved conversation have a unique id, it default way is that companion will use the last "
                    "saved conversation unless specified otherwise to use another saved conversion" 
                    "every prompt without --save-chat will be stateless "
                    "example: jarvis.py 'how are you' --> this is stateless and will not be saved "
                    "example: jarvis.py 'how are you' --save-chat --> this will be saved "
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-p', '--prompt',
                        help='Prompt Jarvis, aks anything')
    group.add_argument('-lc', '--list-chats', action="store_true", help="List chat IDs to use as context")

    parser.add_argument('-md', '--markdown',
                        action="store_true",
                        help="Whether to stream LLM's response as plain text or markdown (Default: True)")
    parser.add_argument('-v', '--verbose',
                        action="store_true", default=False,
                        help="Display detail of server and LLM status (Default: False)")
    parser.add_argument('-s', '--save-chat', action="store_true",
                        help="This option will you save chat from this point on")
    parser.add_argument('-c', '--context', default=None,
                        help="The context to use for this chat (provide chat id uuid)")
    args = parser.parse_args()
    main()
