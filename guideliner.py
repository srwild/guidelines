import math

pageSizes = ("Letter", "Legal", "Tabloid", "A3", "A4")

# Variable UI using vanilla
Variable([
    dict(name="pageSize", ui="PopUpButton", args=dict(items=pageSizes)),
    dict(name="landscape", ui="CheckBox", args=dict(value=True)),
    dict(name="pageMargin_inches", ui="EditText", args=dict(text=".25")),
    dict(name="nib_mm", ui="EditText", args=dict(text="3.8")),
    dict(name="ascender", ui="EditText", args=dict(text="3")),
    dict(name="xHeight", ui="EditText", args=dict(text="4")),
    dict(name="descender", ui="EditText", args=dict(text="3")),
    dict(name="spacing", ui="Slider", args=dict(value=.75, minValue=0, maxValue=5)),
    dict(name="slantGuides", ui="CheckBox", args=dict(value=True)),
    dict(name="slantDegrees", ui="EditText", args=dict(text="10")),
], globals())

# main settings
nibSizeMM = float(nib_mm)
ascender = float(ascender)
xHeight = float(xHeight)
descender = float(descender)
slantState = slantGuides
slant = float(slantDegrees)

# Convert page margin from inches to points
margin = float(pageMargin_inches) * 72

guideStroke = .5
guideStrokeColor = 0

# Converts nib width in mm to points and subtracts guide line thinkness so square is accurate
nibWidth = (nibSizeMM * 2.835) - (guideStroke * 2)

# Set page dimensions
def pageDimensions():
    if landscape:
        return pageSizes[pageSize] + "Landscape"
    else:
        return pageSizes[pageSize]

size(pageDimensions())

# Total guide height
guideHeight = nibWidth * (ascender + xHeight + descender)
# Total guide height with padding
guideHeightPadded = nibWidth * float(spacing) + guideHeight

# calculates how many guides with padding can fit on a page
repeat = int((height() - margin * 2) / guideHeightPadded)

# Calculates bottom margin to center guide set on page
guideMargin = (height() - (guideHeightPadded * repeat)) / 2 + (nibWidth / 2)


def guide(scale):
    divisions = int(scale)
    remainder = scale - divisions
    left = width() - (margin * 2)
    square = nibWidth, nibWidth

    # colors
    fill(guideStrokeColor)
    stroke(guideStrokeColor)
    strokeWidth(guideStroke)

    # Where to start based on previous guide set
    y = start

    # Forces the squares to alternate when previous guide set is odd or fractional
    n = previous
    # Rounds up floats
    if n % 1 > 0:
        n = int(n) + 1
    if n % 2 == 0:
        z = 1
    else:
        z = 0
    # Draw top and bottom guide
    line((nibWidth, y), (left, y))
    line((nibWidth, y + nibWidth * scale), (left, y + nibWidth * scale))

    for i in range(divisions):
        if (i + z) % 2 == 0:
            rect(0, y, *square)
        else:
            rect(nibWidth, y, *square)
        y += nibWidth

    if remainder:
        y2 = nibWidth * remainder
        if (i + z) % 2 == 0:
            rect(nibWidth, y, nibWidth, y2)
        else:
            rect(0, y, nibWidth, y2)
        y += y2


def italic_guide():
    with savedState():
        stroke(.8)
        strokeWidth(guideStroke)

        # Slant guide options
        slantRepeat = 15
        slantSpace = (width() - (margin * 2)) / slantRepeat

        # Variables for calculating slant with right triangle trig formula (This was hard for a high school drop out)
        B = math.radians(slant)
        A = math.radians(90) - B
        a = guideHeight
        c = a / math.sin(A)
        b = c * math.cos(A)

        x = nibWidth * 2.5
        x2 = x + b
        y2 = a

        for i in range(slantRepeat):
            line((x, 0), (x2, y2))
            x += slantSpace
            x2 += slantSpace


with savedState():
    translate(margin, guideMargin)
    for x in range(repeat):
        if slantState == 1:
            italic_guide()
        previous = 0
        start = previous
        guide(descender)
        previous = descender
        start = previous * nibWidth
        guide(xHeight)
        previous = xHeight + descender
        start = previous * nibWidth
        guide(ascender)
        translate(0, guideHeightPadded)

fontSize(5)
text("Nib: " + str(nibSizeMM) + "mm • Scale: " + str(int(ascender)) +
     "/" + str(int(xHeight)) + "/" + str(int(descender)), (margin, margin))

fill(1)
rect(width() - margin, 0, margin, height())

saveImage("guide-sheets/guidelines.pdf")
