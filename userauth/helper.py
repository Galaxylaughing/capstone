def validate_user_fields(fields):
    username = fields.get('username', None)
    password = fields.get('password', None)

    return_dict = {}
    return_dict['errors'] = {}

    if username: # username exists
        return_dict['username'] = username
    else:
        return_dict['username'] = None
        return_dict['errors']['username'] = 'username is missing or empty'

    if password: # password exists
        return_dict['password'] = password
    else:
        return_dict['password'] = None
        return_dict['errors']['password'] = 'password is missing or empty'

    return return_dict


def stringify_errors(errors):
  stringified = ''
  count = len(errors)

  if count == 1:
    stringified += 'Error: '
  else:
    stringified += 'Errors: '

  error_messages = errors.values()
  joiner = ', '
  stringified += joiner.join(error_messages)

  return stringified
