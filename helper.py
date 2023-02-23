from datetime import datetime


def convert_date_string(input_date_string: str) -> str:
    input_formats = ["%m/%d/%Y", "%d.%m.%Y", "%B %d, %Y"]
    # Loop through the input formats and try to parse the date string
    for fmt in input_formats:
        try:
            date_obj = datetime.strptime(input_date_string, fmt)
            # If parsing succeeds, break out of the loop
            break
        except ValueError:
            pass
    else:
        # If none of the input formats work, raise an error
        raise ValueError("Invalid date format")
    return date_obj.strftime("%Y-%m-%d")
