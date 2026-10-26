"""DumDana v2 identity: professional, trust-first."""
FOREST = "#123F2F"
INK = "#10241B"
SAGE = "#EEF3EF"
AMBER = "#C98A2B"
WHITE = "#FFFFFF"

SW = 15  # stroke width of the logotype


def _letters():
    D = 'M7.5,7.5 H30 A37.5,37.5 0 0 1 30,82.5 H7.5 Z'
    u = 'M7.5,30 V60 A22.5,22.5 0 0 0 52.5,60 V30 M52.5,30 V90'
    m = ('M7.5,90 V30 M7.5,57.5 A20,20 0 0 1 47.5,57.5 V90 '
         'M47.5,57.5 A20,20 0 0 1 87.5,57.5 V90')
    a = 'M52.5,60 A22.5,22.5 0 1 1 52.5,59.99 M52.5,30 V90'
    n = 'M7.5,90 V30 M7.5,57.5 A22.5,22.5 0 0 1 52.5,57.5 V90'
    seq = [(D, 0), (u, 87), (m, 159), (D, 266), (a, 353), (n, 425), (a, 497)]
    return "".join(f'<path transform="translate({x},0)" d="{d}"/>' for d, x in seq)


def wordmark(color=FOREST):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -2 557 94" role="img" aria-label="DumDana">'
            f'<g fill="none" stroke="{color}" stroke-width="{SW}" stroke-linecap="butt" stroke-linejoin="miter">'
            f'{_letters()}</g></svg>')


def mark_inner(fg=WHITE, dot=AMBER):
    return (f'<path d="M31,25 H48 A25,25 0 0 1 48,75 H31 Z" fill="none" stroke="{fg}" stroke-width="12" stroke-linejoin="miter"/>'
            f'<circle cx="52" cy="50" r="8.5" fill="{dot}"/>')


def mark(bg=FOREST, fg=WHITE, dot=AMBER, shape="square"):
    b = (f'<rect width="100" height="100" rx="20" fill="{bg}"/>' if shape == "square"
         else f'<circle cx="50" cy="50" r="50" fill="{bg}"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">{b}{mark_inner(fg, dot)}</svg>'


def lockup(color=FOREST):
    """Mark + wordmark side by side, one SVG."""
    m = mark().replace('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">',
                       '<svg x="0" y="0" width="100" height="100" viewBox="0 0 100 100">')
    w = wordmark(color).replace('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -2 557 94" role="img" aria-label="DumDana">',
                                '<svg x="128" y="12" width="420" height="71" viewBox="0 -2 557 94">')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 552 100" role="img" aria-label="DumDana">{m}{w}</svg>'
