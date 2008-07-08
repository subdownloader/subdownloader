//based on http://arnfast.net/projects/ifoinfo.php by Jens Arnfast 

#include <Python.h>

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <unistd.h>
#include <assert.h>

#include <dvdread/dvd_reader.h>
#include <dvdread/ifo_types.h>
#include <dvdread/ifo_read.h>

static PyObject *ifoinfo_open(PyObject *self, PyObject *args);
static PyObject *ifoinfo_close(PyObject *self, PyObject *args);

static PyObject *ifoinfo_read_title(PyObject *self, PyObject *args);
static PyObject *ifoinfo_get_audio_tracks(PyObject *self, PyObject *args);
static PyObject *ifoinfo_get_subtitle_tracks(PyObject *self, PyObject *args);

static PyMethodDef IfoMethods[] = {
  {"open",  ifoinfo_open, METH_VARARGS},
  {"close",  ifoinfo_close, METH_VARARGS},
  {"title", ifoinfo_read_title, METH_VARARGS},
  {"audio", ifoinfo_get_audio_tracks, METH_VARARGS},
  {"subtitle", ifoinfo_get_subtitle_tracks, METH_VARARGS},
  {NULL, NULL}
};


void initifoparser() {
   (void) Py_InitModule("ifoparser", IfoMethods);
}


dvd_reader_t *dvd;
ifo_handle_t *ifofile;

static PyObject *ifoinfo_open(PyObject *self, PyObject *args) {
  tt_srpt_t *tt_srpt;
  int i, ch, gotopt = -1, dochapters = -1;
  char *dvddevice;

  if (!PyArg_ParseTuple(args, "s", &dvddevice))
    return Py_BuildValue("i", 0);

  dvd = DVDOpen(dvddevice);
  
  if (!dvd)
    return Py_BuildValue("i", 0);
  
  ifofile = ifoOpen(dvd, 0);
  if (!ifofile) {
    DVDClose(dvd);
    return Py_BuildValue("i", 0);
  }

  tt_srpt = ifofile->tt_srpt;
  return Py_BuildValue("i", tt_srpt->nr_of_srpts);
}


static PyObject *ifoinfo_close(PyObject *self, PyObject *args) {
  ifoClose(ifofile);
  DVDClose(dvd);
  return Py_BuildValue("i", 0);
}


static PyObject *ifoinfo_read_title(PyObject *self, PyObject *args) {
  int i;

  tt_srpt_t *tt_srpt;
  ifo_handle_t *vtsfile;
  int vtsnum, ttnnum, j;
  long playtime;

  if (!PyArg_ParseTuple(args, "i", &i))
    return Py_BuildValue("(iiiii)", 0, 0, 0, 0, 0);

  i--;
  
  tt_srpt = ifofile->tt_srpt;
  vtsnum  = tt_srpt->title[i].title_set_nr;
  ttnnum  = tt_srpt->title[i].vts_ttn;
     
  vtsfile = ifoOpen(dvd, vtsnum);
    
  if (!vtsfile)
    return Py_BuildValue("(iiiii)", 0, 0, 0, 0, 0);

  playtime = 0;
  
  if (vtsfile->vts_pgcit) {
    dvd_time_t *ttime;
    ttime = &vtsfile->vts_pgcit->pgci_srp[0].pgc->playback_time;
    playtime = ((ttime->hour * 60) + ttime->minute) * 60 + ttime->second;
  }

  // Number of Chapters, Number of Angles, Playback time, Num Audio tracks,
  // Num subtitles
  return Py_BuildValue("(iiiii)", tt_srpt->title[i].nr_of_ptts,
		       tt_srpt->title[i].nr_of_angles, playtime,		       
		       vtsfile->vtsi_mat->nr_of_vts_audio_streams,
		       vtsfile->vtsi_mat->nr_of_vts_subp_streams);
}


static PyObject * ifoinfo_get_subtitle_tracks(PyObject *self, PyObject *args) {
  char language[5];
  int trackno;
  tt_srpt_t *tt_srpt;
  int vtsnum, ttnnum;
  ifo_handle_t *vtsfile;
  int i;
  subp_attr_t *attr;
  
  if (!PyArg_ParseTuple(args, "ii", &i, &trackno))
    return Py_BuildValue("(s)", "N/A");

  i--;
  trackno--;
  
  tt_srpt = ifofile->tt_srpt;
  vtsnum = tt_srpt->title[i].title_set_nr;
  ttnnum = tt_srpt->title[i].vts_ttn;
  
  vtsfile = ifoOpen(dvd, vtsnum);
  
  if (vtsfile->vts_pgcit) {
    attr = &vtsfile->vtsi_mat->vts_subp_attr[trackno];

    if ( attr->type == 0
	 && attr->lang_code == 0
	 && attr->zero1 == 0
	 && attr->zero2 == 0
	 && attr->lang_extension == 0 ) {
      return Py_BuildValue("(s)", "N/A");
    }

    /* language code */
    if (isalpha((int)(attr->lang_code >> 8)) && isalpha((int)(attr->lang_code & 0xff))) {
      snprintf(language, 5, "%c%c", attr->lang_code >> 8, attr->lang_code & 0xff);
    } else {
      snprintf(language, 5, "%02x%02x", 0xff & (unsigned)(attr->lang_code >> 8), 
	       0xff & (unsigned)(attr->lang_code & 0xff));
    }

    return Py_BuildValue("(s)", language);
  }
}


static PyObject * ifoinfo_get_audio_tracks(PyObject *self, PyObject *args) {
  char audioformat[10];
  char audiolang[5];
  int audiochannels;
  int audioid;
  int audiofreq;
  audio_attr_t *attr;
  int i;
  int trackno;
  tt_srpt_t *tt_srpt;
  int vtsnum, ttnnum;
  ifo_handle_t *vtsfile;
  
  if (!PyArg_ParseTuple(args, "ii", &i, &trackno))
    return Py_BuildValue("i", 0);

  i--;
  trackno--;
  
  tt_srpt = ifofile->tt_srpt;
  vtsnum = tt_srpt->title[i].title_set_nr;
  ttnnum = tt_srpt->title[i].vts_ttn;
  
  vtsfile = ifoOpen(dvd, vtsnum);
  
  if (vtsfile->vts_pgcit && vtsfile->vtsi_mat) {
    attr = &vtsfile->vtsi_mat->vts_audio_attr[trackno];

    audioid = trackno + 128;
    
    if ( attr->audio_format == 0
	 && attr->multichannel_extension == 0
	 && attr->lang_type == 0
	 && attr->application_mode == 0
	 && attr->quantization == 0
	 && attr->sample_frequency == 0
	 && attr->channels == 0
	 && attr->lang_extension == 0
	 && attr->unknown1 == 0
	 && attr->unknown1 == 0) {
      snprintf(audioformat, 10, "Unknown");
      return Py_BuildValue("i", 0);
    }
    
    /* audio format */
    switch (attr->audio_format) {
    case 0:
      snprintf(audioformat, 10, "ac3");
      break;
    case 1:
      snprintf(audioformat, 10, "N/A");
      break;
    case 2:
      snprintf(audioformat, 10, "mpeg1");
      break;
    case 3:
      snprintf(audioformat, 10, "mpeg2ext");
    break;
    case 4:
      snprintf(audioformat, 10, "lpcm");
      break;
    case 5:
      snprintf(audioformat, 10, "N/A");
      break;
    case 6:
      snprintf(audioformat, 10, "dts");
      break;
    default:
      snprintf(audioformat, 10, "N/A");
    }
    
    switch (attr->lang_type) {
    case 0:
      assert(attr->lang_code == 0 || attr->lang_code == 0xffff);
      snprintf(audiolang, 5, "N/A");
      break;
    case 1:
      snprintf(audiolang, 5, "%c%c", attr->lang_code>>8, attr->lang_code & 0xff);
      break;
    default:
      snprintf(audiolang, 5, "N/A");
    }
    
    switch(attr->sample_frequency) {
    case 0:
      audiofreq = 48;
      break;
    case 1:
      audiofreq = -1;
      break;
    default:
      audiofreq = -1;
    }
    
    audiochannels = attr->channels + 1;
    
    //AUDIOTRACK: ID=%i; LANG=%s; FORMAT=%s; CHANNELS=%i; FREQ=%ikHz
    return Py_BuildValue("(issii)", audioid, audiolang, audioformat, audiochannels,
			 audiofreq);
  }

  return NULL;
}

