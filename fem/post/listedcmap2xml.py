def listedcmap2xml(cmap):
    """Convert ListedColormap to XML format for import into Paraview

    Based on: https://www.paraview.org/Wiki/Colormaps

    Args:
        ListedColormap (ListedColormap): Matplotlib-formated ListedColormap
    """
    N = len(cmap.colors)
    with open('{}.xml'.format(cmap.name), 'w') as f:
        f.write('<ColorMap name="{}" space="HSV">\n'.format(cmap.name))
        for n, i in enumerate(cmap.colors):
            f.write('  <Point x="{:f}" o="1" r="{:f}" g="{:f}" b="{:f}"/>\n'
                    .format(((n) / (N - 1)), *i))
        f.write('</ColorMap>')
