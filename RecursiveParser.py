# Python is a feature-rich language and it can also be extended via libraries.  In
# this file, we need to include functionality inside the "os" library module.  We
# include this library by typing "import os"
import os

# Creating classes in Python is easy.  Simply declare it as shown below and indent
# everything that belongs in the class.
#
# On another note, you may have noticed I comment everything using the # mark
# and that my comments appear above the code that they discuss.  You may have also
# noticed the comment listed below the line "class RecursiveParser:" that uses three
# single quote marks to designate the beginning and end of the comment.  These are
# special comments that can be used to self-document your classes and methods for
# use in PyDoc documentation and IDEs that support them for things like automatic
# line completion, etc.  They must appear BELOW the class, function, and method
# declarations they are associated with.
class RecursiveParser:
    '''
    The RecursiveParser class contains methods to recursively find directories, files, or specific files in a
    directory structure
    '''
    
    # The getRecursiveDirList() method accepts a directory path as an argument and
    # then recursively searches through that path looking for directories to return
    # to you in the form of a list.
    #
    # If you look at the bottom of the file on line ????????, you will notice we
    # are only passing one argument (a directory path) to this method.  However, 
    # when we declare the method here, we are specifying two arguments.
    #
    # This is, in my opinion, an oddity with Python classes.  If this
    # method were a stand-alone function outside of a class, then you would not need the
    # "self" argument.  The reasons for this oddity are beyond the scope of this tutorial so
    # just take in on faith for now that whenever you create a method inside of a class,
    # its first argument must be "self", followed by any other arguments you wish to add.
    def getRecursiveDirList(self, basedir):
        '''
        getRecursiveDirList takes a directory in the form of a string and returns a list of all
        subdirectories contained therein
        (e.g. getRecursiveDirList('/home/user/files')
        '''
        # I want all of my directory paths to have a trailing slash (e.g. /home/user/documents/).
        # However, if I add the ability to this code to accept command line arguments, I can't
        # guarantee that all users of my code will add this slash.  Therefore, I have created a
        # method that checks to see if the trailing slash exists and appends one if it does not.
        basedir = self.addSlash(basedir)
            
        # Here we specify two variables.  subdirlist keeps a list of all the directories contained
        # within the current directory and dirlist keeps a running list of all the directories found
        # throughout the entire directory structure.
        subdirlist = []
        dirlist = []
        
        # Since we know that the argument "basedir" is a directory (or should be) we will add it to
        # the dirlist variable.
        dirlist.append(basedir)
        
        # Next, we are going to list all the contents of the current directory and then check each
        # item one at a time to see if it is a directory or a file.  If it is a directory, then we
        # will add it to the dirlist variable (our final, definitive list of all directories contained in a
        # given path) and also the subdirlst variable (a list of directories we still need to check).
        #
        # Since things can go wrong, like a user mistakenly entering their first name instead of a valid
        # directory, we need to place this code within a try: except: statement.  If we didn't do this,
        # and a user entered invalid data, our program would crash.  By placing error handling
        # around our code like this, we are able to print out a friendly, trust-inspiring message
        # to the user instead of a bleak stack trace.  In this case, I'm only catching a "WindowsError",
        # which is sort of robust, but not really.
        try:
            for item in os.listdir(basedir):
                if os.path.isdir(os.path.join(basedir, item)):
                    dirlist.append(os.path.join(basedir, item))
                    subdirlist.append(os.path.join(basedir, item))
                    
        # There are, of course, other exception types and a generic except statement that can
        # catch all errors.  The generic would look like "except:".  I ran into a permission
        # issue on my Windows machine when I ran this script, so I thought I'd use the WindowsError
        # exception as an example of catching a specific type of error.
        #
        # Using specific exception types in your error handling allows you to customize
        # error messages for each type of error that occurs instead of always printing
        # a generic "Something went wrong but I don't know what it was" type of error.
        except WindowsError:
            print "An error has occured.  You may not have permission"
            print "to access all files and folders in the specified path."
            
        # Now we need to recursively call getRecursiveDirList until you reach the end of
        # the directory structure.  This means that getRecursiveDirList will call itself
        # over and over again until there are no more subdirectories left to process.
        for subdir in subdirlist:
            dirlist += self.getRecursiveDirList(subdir)
            
        # Return a comprehensive list of all directories contained within 'basedir' 
        return dirlist
        
    # The getRecursiveFileList() method accepts a directory path as an argument and
    # then recursively searches through that path looking for files to return
    # to you in the form of a list.
    #
    # Notice that this method also has "self" as its first argument.  This is because
    # it is also part of a class.  If it were a stand-alone function, we wouldn't need
    # this argument.  In fact, our program would probably crash if we had it there in
    # that case.
    #
    # You probably noticed that getRecursiveFileList has one more parameter than
    # getRecursiveDirList has (extensions=[]).  This allows us to limit the list of
    # files to a certain extension, or list of extensions.  For example, if I
    # called this method like this:
    #       getRecursiveFileList('/home/user/documents', ['html', 'htm', 'txt'])
    # then the method would only return files to me that had those three extensions.
    #
    # On the other hand, I don't want to have to type ALL possible extensions when
    # I want absolutely everything, so I declare the extensions variable like this:
    #        extensions=[]
    # This means that "extensions" is optional.  The method will take whatever
    # extensions I give it, but if I choose to leave them off, it will default
    # to an empty list, which my code interprets to mean "everything".
    #
    # You can make any parameter optional by appending an equals sign to it and
    # following that with a default value (e.g. printName(fname="unknown", lname="unknown")).
    #
    # IMPORTANT NOTE: Python orders the variables you pass to a method by applying the
    # first variable to the first item in the method's parameter list, second to second,
    # and so forth.  So, if you had this method:
    #        printName(fname="unknown", lname="unknown")
    # and you were trying to print a name, but you only knew the last name, Smith, you
    # couldn't just type "printName("Smith") because Python would assign the last name
    # Smith to the fname (first name) variable; which isn't what you want.
    #
    # In this case, to get the variables to align correctly, you would have to either type
    # "printName("unknown", "Smith"), which doesn't take advantage of your optional parameters,
    # or better yet, type "printName(lname="Smith)".  This will assign smith to the lname variable
    # and let the fname variable revert to its default value automatically.
    def getRecursiveFileList(self, basedir, extensions=[]):
        '''
        getRecursiveFileList takes a directory in the form of a string and returns a list of all
        of the files contained therein.  If you would like to search only for specific file
        extensions, pass a list of extensions as the second argument
        (e.g. getRecursiveFileList('/home/user/files', ['htm', 'html', 'css'])
        '''
        # Add a trailing slash if one doesn't alreay exist
        # You have already seen the next three lines of code.  Refer to
        # getRecursiveDirList() if you have forgotten what they are for.
        basedir = self.addSlash(basedir)
        
        subdirlist = []
        filelist = []
        
        # This code is almost identical to the try: except: segment of getRecursiveDirList().
        # The differences here are that instead of directories, we are searching for files
        # and adding them to the definitive list "filelist".
        try:
            # First, we check to see if the "extensions" variable has any items in it.  If
            # it does, then we first check to see if the current item is a file or not, and
            # if it is a file, we check to see if its extension is one of the ones specified
            # in the "extensions" variable.  If all these tests pass, then we add the file
            # to the file list.  If not, we don't.
            if len(extensions) > 0:
                for item in os.listdir(basedir):
                    if os.path.isfile(os.path.join(basedir, item)):
                        if extensions.count(item[item.rfind('.') + 1:]) > 0:
                            filelist.append(os.path.join(basedir, item))
                    else:
                        subdirlist.append(os.path.join(basedir, item))
            # If the "extensions" variable is empty, then we add anything that is a file to
            # "filelist".
            else:
                for item in os.listdir(basedir):
                    if os.path.isfile(os.path.join(basedir, item)):
                        filelist.append(os.path.join(basedir, item))
                    else:                        
                        subdirlist.append(os.path.join(basedir, item))
                        
        # Here again you can see an example of catching a specific type of error.  In this
        # example, I am catching both a WindowsError exception and also a TypeError exception
        # While my error messages are probably lame, this shows that you can customize your
        # error handling in order to let your users (or you yourself) know what is going on when
        # a problem occurs while running your code.
        #except WindowsError:
            #print "An error has occured.  You may not have permission"
            #print "to access all files and folders in the specified path."
            
        except TypeError:
            print "The calling code has passed an invalid parameter to"
            print "getRecursiveFileList."
        
        # This is an example of a generic catchall for exceptions.
        except:
            print "Failure! Failure! A failure has occured! We don't know"
            print "what failed exactly, but whatever it was, it failed!" 

                    
        # Recursively call getRecursiveDirList until you reach the end of the directory structure
        for subdir in subdirlist:
            filelist += self.getRecursiveFileList(subdir, extensions)
            
        # Return a comprehensive list of all files (or specified files) contained within 'basedir' 
        return filelist

    def addSlash(self, dir):
        '''
        addSlash(dir) adds a trailing slash to a string representation of a directory
        '''        
        # I want to make sure that all the paths I pass to my program have a trailing
        # slash character.  I could have written more code in the methods to handle both
        # cases, but I chose to do it this way in order to keep things simple.
        if dir[-1:] != '/':
            dir += '/'
        
        return dir

# In Python, if you run code directly from the command line, the internal variable
# __name__ will have a value of "__main__".  If you call the file via an "include"
# statement to use it within some other code, then "__name__" will be something else.
#
# This is nice because it lets you add code to all your files that will run when called
# from the command line, but will not run when your code is used as a library.  You can
# use this to add unit testing to library files.  When you run your libraries from the
# command line, then your unit tests will run, but when a user imports your library
# into their code, your unit test code is ignored.
#
# We do this by using the statement "if __name__ == '__main__':".  Anything contained
# within this code block will be executed when the file is run from the command line
# and ignored when it is run in any other way.
#
# While this is not serious unit testing, it demonstrates a good strategy and
# it will exercise the two main methods of our class and display the results
# onto the screen (in an albeit ugly way). 
#if __name__ == '__main__':
    ## This is how you create an instance of your RecursiveParser class
    #parser = RecursiveParser()
    
    ## Replace /home/user/documents with whichever path you wish to search
    #print 'PRINTING DIRECTORIES\n'
    #dirs = parser.getRecursiveDirList('/home/user/documents')
    #print dirs
    
    ## Replace /home/user/documents with whichever path you wish to extract a list of files from
    ## Remember that the extensions argument is optional.  If you leave it off the returned list
    ## contain a list of all the files in the specified directory.
    #print 'PRINTING ALL FILES\n'
    #files = parser.getRecursiveFileList('/home/user/documents')
    #print files
    
    ## Here is an example that specifies some file extensions.
    #print 'PRINTING ALL HTML, TXT, and DOC FILES\n'
    #files = parser.getRecursiveFileList('/home/user/documents', ['html', 'txt', 'doc'])
    #print files
    
    ## Finally, here is an example that specifies only one file extension.  Note that even
    ## when there is only one file extension, it still needs to be in a list
    #print 'PRINTING ALL HTML FILES\n'
    #files = parser.getRecursiveFileList('/home/user/documents', ['html'])
    #print files
    