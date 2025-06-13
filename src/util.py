"""Util file providing utilities functions"""

import cProfile
import io
import pstats
from functools import wraps


def profile_this_endpoint(f):
    """
    This decorator profile the given function and save a report in /profile_data
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = f(*args, **kwargs)
        pr.disable()

        s = io.StringIO()
        sortby = "cumulative"
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()

        # Save the profile data to a file
        profile_filename = f"profile_data/{f.__name__}.prof"
        pr.dump_stats(profile_filename)
        print(f"Profile saved to {profile_filename}")

        # Save the report to a text file
        report_filename = f"profile_data/{f.__name__}_report.txt"
        with open(report_filename, "w") as f_report:
            f_report.write(s.getvalue())
        print(f"Profile report saved to {report_filename}")

        # Optionally print to console
        # print(s.getvalue())

        return result

    return decorated_function
