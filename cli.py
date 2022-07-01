import click

@click.command()
@click.option('-i', '--input',      help='Source video path', required=True)
@click.option('-o', '--output',     help='Path of the generated synopsis', required=True)
@click.option('-q',                 help="q parameter of L(q)-coloring problem.", default=3, show_default=True)
def synopsis(i, o, q):
    pass

if __name__ == '__main__': synopsis()