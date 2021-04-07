from config import *

if not windowMode:
    print 'Screen mode: Fullscreen'
else:
    print 'Screen mode: {}'.format(str(windowSize))

print ''
print '###################### Experimental design'
print '# '
print '# Matrix size: {}'.format(str(matrixSize))
print '# Cards size: {}'.format(str(cardSize))
print '# Number of maximum blocks: {}'.format(str(nbBlocksMax))
print '# Maximum correct answers: {}'.format(str(correctAnswersMax))

print ''
print '###################### Rest/Wait periods'
print '# '
print '# Presentation card: {} ms'.format(str(presentationCard))
print '# Presentation cue: {} ms'.format(str(presentationCard))
print '# Time to respond: {} ms'.format(str(responseTime))
print '# Rest period between blocks: {} ms'.format(str(restPeriod))

print ''
print '###################### Colors'
print '# '
print '# Background color: {}'.format(str(bgColor))
print '# Cards color: {}'.format(str(cardColor))
print '# Cue Card color: {}'.format(str(cueCardColor))
print ''


raw_input("Press Enter to continue...")