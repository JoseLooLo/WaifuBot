def compare_names(waifu_name, waifu_nickname, user_input):
    if len(user_input) == 0:
        return False

    counter = 0

    waifu_token_name = waifu_name.split(" ")
    for i in range(len(waifu_token_name)):
        waifu_token_name[i] = waifu_token_name[i].lower()
    
    user_input_token = user_input  #user_input.split(" ")
    for i in range(len(user_input_token)):
        user_input_token[i] = user_input_token[i].lower()

    for i in range(len(user_input_token)):
        if user_input_token[i] in waifu_token_name:
            waifu_token_name.remove(user_input_token[i])
            counter += 1
    
    if len(waifu_token_name) == 0 or counter >= 1:
        return True

    return False