import math
from AppKit import NSColor

# Default guide colors
_initial_guide_color = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1)
_initial_slant_color = NSColor.colorWithCalibratedRed_green_blue_alpha_(.6, .6, .6, 1)

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
    dict(name="drawSquares", ui="CheckBox", args=dict(value=True)),
    dict(name="guide_color", ui="ColorWell", args=dict(color=_initial_guide_color)),
    dict(name="slant_color", ui="ColorWell", args=dict(color=_initial_slant_color))
], globals())

def variableCheck(variable):
    '''
    Change variable in UI to float, if empty return 0.
    Prevents error if values are deleted from the field.
    '''
    if variable:
        return float(variable)
    else:
        return 0

# main settings
nibSizeMM = variableCheck(nib_mm)
ascender = variableCheck(ascender)
xHeight = variableCheck(xHeight)
descender = variableCheck(descender)
slant = variableCheck(slantDegrees)

# Convert page margin from inches to points
margin = variableCheck(pageMargin_inches) * 72

# Stroke Settings
guideStroke = .5
guideStrokeColor = guide_color
slantStroke = guideStroke
slantStrokeColor = slant_color

# Converts nib width to points
nibWidth = (nibSizeMM * 2.8346456693)

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

    # Draw lines
    with savedState():
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
        line((0, y), (left, y))
        line((0, y + nibWidth * scale), (left, y + nibWidth * scale))

    # Draw squares
    if drawSquares == True:
        with savedState():
            fill(guideStrokeColor)

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
        stroke(slantStrokeColor)
        strokeWidth(slantStroke)

        # Slant guide options
        slantRepeat = 15
        lineSpacing = (width() - (margin * 2) - (nibWidth * 2)) / slantRepeat

        # Variables for calculating slant with right triangle trig formula (This was hard for a high school drop out)
        B = math.radians(slant)
        A = math.radians(90) - B
        a = guideHeight
        c = a / math.sin(A)
        b = c * math.cos(A)


        translate(nibWidth * 2, 0)
        for i in range(slantRepeat):
            line((0, 0), (b, a))
            translate(lineSpacing, 0)


with savedState():
    translate(margin, guideMargin)
    for x in range(repeat):
        if slantGuides == 1:
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


# Make a slug
def slugNumber(number):
    '''
    Change number to integer if it's a whole number
    '''
    if number % 1 > 0:
        return str(number)
    else:
        return str(int(number))
slugText = ["Nib: ", slugNumber(nibSizeMM), "mm • Scale: ",
            "/".join([slugNumber(ascender), slugNumber(xHeight), slugNumber(descender)])]
fontSize(5)
text("".join(slugText), (margin, margin))


# Mask parts of slant guides that overshoot into the margin
fill(1)
rect(width() - margin, 0, margin, height())


# *******************
saveImage("guide-sheets/guidelines.pdf")
