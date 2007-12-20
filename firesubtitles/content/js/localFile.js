var localFile = {
  init : function(path) {
    try {
      var file = Components.classes['@mozilla.org/file/local;1'].createInstance(Components.interfaces.nsILocalFile);
      file.initWithPath(path);
      return file;
    } catch (ex) {
      return null;
    }
  },

  launch : function(file) {
    try {
      if (file.exists()) {
        file.launch();
      }
    } catch (ex) {
      debug(ex);
    }
  },

  create : function(isDir, name) {
    var dir = this.init(localTree.constructPath(gLocalPath.value, name));

    try {
      dir.create(isDir ? Components.interfaces.nsILocalFile.DIRECTORY_TYPE : Components.interfaces.nsILocalFile.NORMAL_FILE_TYPE,
                 isDir ? 0755 : 0644);
    } catch (ex) {
      debug(ex);
      error(gStrbundle.getString(isDir ? "dirFail" : "fileFail"));
      return null;
    }

    return dir;
  },

  remove : function(file, prompt, multiple) {
    if (prompt && multiple && multiple > 1) {                                           // deleting multiple
      if (!window.confirm(gStrbundle.getFormattedString("confirmDelete2", [multiple]) + '\n'
                        + gStrbundle.getString("localDeleteWarning"))) {
        return false;
      }
    } else if (prompt && file.isDirectory()) {                                          // deleting a directory
      if (!window.confirm(gStrbundle.getFormattedString("confirmDelete3", [file.leafName]) + '\n'
                        + gStrbundle.getString("localDeleteWarning"))) {
        return false;
      }
    } else if (prompt) {                                                                // deleting a file
      if (!window.confirm(gStrbundle.getFormattedString("confirmDelete", [file.leafName]) + '\n'
                        + gStrbundle.getString("localDeleteWarning"))) {
        return false;
      }
    }

    try {
      ++gProcessing;
      var innerEx = gFireFTPUtils.removeFile(file);
      --gProcessing;

      if (innerEx) {
        throw innerEx;
      }
    } catch (ex) {
      debug(ex);
      error(gStrbundle.getString("delFail"));
      return false;
    }

    return true;
  },

  rename : function(file, newName) {
    if (!file.exists()) {
      return false;
    }

    if (!newName || file.leafName == newName) {
      return false;
    }

    var oldName = file.leafName;

    try {
      var newFile = this.init(file.parent.path);
      newFile.append(newName);

      if (newFile && newFile.exists() && (gSlash == '/' || oldName.toLowerCase() != newName.toLowerCase())) {
        error(gStrbundle.getString("renameFail"));
        return false;
      }

      file.moveTo(null, newName);                                                       // rename the file
    } catch (ex) {
      if (gSlash == '\\' && oldName.toLowerCase() == newName.toLowerCase()) {           // we renamed the file the same but with different case
        return true;                                                                    // for some reason this throws an exception
      }

      debug(ex);
      error(gStrbundle.getString("renameFail"));
      return false;
    }

    return true;
  },

  showProperties : function(file, recursive) {
    try {
      var date = new Date(file.lastModifiedTime);
      date     = gMonths[date.getMonth()] + ' ' + date.getDate() + ' ' + date.getFullYear() + ' ' + date.toLocaleTimeString();

      var recursiveFolderData = { type: "local", nFolders: 0, nFiles: 0, nSize: 0 };

      if (file.isDirectory() && recursive) {
        localTree.getRecursiveFolderData(file, recursiveFolderData);
      }

      var origWritable = file.isWritable();

      var params = { path                : file.path,
                     leafName            : file.leafName,
                     fileSize            : file.fileSize,
                     date                : date,
                     origPermissions     : gSlash == "/" ? "-" + localTree.convertPermissions(false, file.permissions) : 0,
                     permissions         : "",
                     writable            : file.isWritable(),
                     hidden              : file.isHidden(),
                     isDirectory         : file.isDirectory(),
                     multipleFiles       : false,
                     isLinuxType         : gSlash == "/",
                     isLocal             : true,
                     recursiveFolderData : file.isDirectory() && recursive ? recursiveFolderData : null,
                     returnVal           : false,
                     isSymlink           : file.isSymlink(),
                     symlink             : file.isSymlink() ? file.target : "" };

      window.openDialog("chrome://fireftp/content/properties.xul", "properties", "chrome,modal,dialog,resizable,centerscreen", params);

      if (!params.returnVal) {
        return false;
      }

      if (params.isLinuxType) {
        if (params.permissions) {
          if (gMac) {
            var perm         = (file.isDirectory() ? "4" : "10") + params.permissions;
            file.permissions = parseInt(perm, 8);
          } else {
            file.permissions = parseInt(params.permissions, 8);
          }
          return true;
        }
      } else if (origWritable != params.writable) {
        if (params.writable) {
          file.permissions = file.permissions == 365 ? 511 : 438;
        } else {
          file.permissions = file.permissions == 511 ? 365 : 292;
        }

        return true;
      }
    } catch (ex) {
      debug(ex);
    }

    return false;
  },

  verifyExists : function(file) {
    var exists = file && file.exists();

    if (!exists && file) {
      error(gStrbundle.getFormattedString("fileDoesNotExist", [file.path]));
    }

    return exists;
  },

  testSize : function(file) {                                                           // XXX in linux, files over 2GB throw an exception
    try {
      var x = file.fileSize;
      return true;
    } catch (ex) {
      return false;
    }
  }
}
