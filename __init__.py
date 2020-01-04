import sys
import os
'''
Because of the path problem I encountered during when consuming
EquimolarBlog on Equimolar website, I this makes sure that files
Equimolar are search for if the files does not exist in the higher
paths.
This might have been left to be fixed by consuming app from
just appending this folder path the search path, but I guess,
I do it here, once and for all.
Note that if EquimolarBlog will be used directly, this file
won't make a difference.
'''
sys.path.append(os.path.abspath(os.path.dirname(__file__)))