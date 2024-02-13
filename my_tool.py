import click
import app.attendance as attendance
import app.personal_info_all_data as info
import app.enrollment as enrollment
import app.cumulative_count as cumulative_count
import app.attendance_special as attendance_special

@click.command()
@click.argument('mode')
@click.option('--o')
@click.option('--c')
@click.option('--filtered')
@click.option('--blacklist', is_flag=True)
@click.option('--am', is_flag=True)
@click.option('--zc')
@click.option('--config')
@click.version_option('1.2.3')
def main(mode, o, c, filtered, blacklist, am, zc, config):
    match mode:
        case 'info':
            pth_in = click.prompt("\n--------------------------------------------------\nenter path to child and family data input folder")
            info.main(pth_in, o)
        case 'attendance':
            pth_in = click.prompt("\n--------------------------------------------------\nenter path to attendance data input folder")
            attendance.main(pth_in, o, filtered, c, am, zc)
        case 'enrollment':
            pth_in = click.prompt("\n--------------------------------------------------\nenter path to enrollment student list file")
            enrollment.main(pth_in, o)
        case 'cumulative':
            pth_in = click.prompt("\n--------------------------------------------------\nenter path to enrollment student list file")
            cumulative_count.main(pth_in, o, blacklist, config)
        case 'attendance_special':
            pth_in = click.prompt("\n--------------------------------------------------\nenter path to attendance data input folder")
            attendance_special.main(pth_in, o, filtered, c, am)
        case _:
            click.echo(f'{mode} is not a supported mode. Type --help for accepted commands.')
        