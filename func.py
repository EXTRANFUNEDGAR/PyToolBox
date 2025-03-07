# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 21:18:09 2024

@author: extranfunedgar
"""

import yt_dlp
from moviepy.editor import AudioFileClip
import os
import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, ID3NoHeaderError

def download_video(video_url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'descargas/%(title)s - %(uploader)s.%(ext)s',  # Formato de nombre
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(result)
            cover_url = download_cover(result)  # Descargar la portada
            if cover_url:
                add_cover_to_mp3(file_path, cover_url)  # Agregar la portada al MP3
            convert_webm_to_mp3(file_path)  # Convertir después de agregar la portada
            return file_path
    except Exception as e:
        print(f"Error al descargar {video_url}: {e}")
        return None

def download_playlist(playlist_url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'descargas/%(playlist)s/%(title)s - %(uploader)s.%(ext)s',  # Formato de nombre
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(playlist_url, download=True)
            for entry in results['entries']:
                file_path = ydl.prepare_filename(entry)
                cover_url = download_cover(entry)  # Descargar la portada
                if cover_url:
                    add_cover_to_mp3(file_path, cover_url)  # Agregar la portada al MP3
                convert_webm_to_mp3(file_path)  # Convertir cada archivo descargado
    except Exception as e:
        print(f"Error al descargar la playlist: {e}")

def convert_webm_to_mp3(webm_file):
    mp3_file = os.path.splitext(webm_file)[0] + ".mp3"
    
    if os.path.exists(webm_file):  # Verifica si el archivo WebM existe
        try:
            audio_clip = AudioFileClip(webm_file)
            audio_clip.write_audiofile(mp3_file, codec='mp3')
            audio_clip.close()
            print(f"Conversión exitosa: {mp3_file} creado.")
            
            # Eliminar el archivo WebM después de agregar la portada
            os.remove(webm_file)
            print(f"Archivo WebM eliminado: {webm_file}")
            
        except Exception as e:
            print(f"Error en la conversión: {e}")
    else:
        print(f"El archivo WebM no se encontró: {webm_file}")

def download_cover(video_info):
    cover_url = video_info.get('thumbnails', [None])[-1]['url'] if video_info.get('thumbnails') else None
    
    if cover_url:
        cover_response = requests.get(cover_url)
        if cover_response.status_code == 200:
            cover_path = os.path.join('descargas', f"{video_info['title']}_cover.jpg")
            with open(cover_path, 'wb') as f:
                f.write(cover_response.content)
            print(f"Portada descargada: {cover_path}")
            return cover_path
        else:
            print("Error al descargar la portada.")
    else:
        print("No se encontró la URL de la portada.")
    return None

def add_cover_to_mp3(mp3_file, cover_path):
    try:
        audio = MP3(mp3_file, ID3=ID3)
        with open(cover_path, 'rb') as cover_file:
            audio.tags.add(APIC(mime='image/jpeg', type=3, desc='Cover', data=cover_file.read()))
        audio.save()
        print(f"Portada agregada al archivo MP3: {mp3_file}")
    except ID3NoHeaderError:
        print("ID3 header no encontrado. Agregando uno nuevo.")
        audio = MP3(mp3_file, ID3=ID3)
        with open(cover_path, 'rb') as cover_file:
            audio.add_tags()
            audio.tags.add(APIC(mime='image/jpeg', type=3, desc='Cover', data=cover_file.read()))
        audio.save()
    except Exception as e:
        print(f"Error al agregar portada al MP3: {e}")

if __name__ == "__main__":
    # Crear directorio de descargas si no existe
    if not os.path.exists('descargas'):
        os.makedirs('descargas')
    
    choice = input("¿Quieres descargar un video o una playlist? (v/playlist): ").strip().lower()

    if choice == 'v':
        video_url = input("Ingresa la URL del video: ")
        download_video(video_url)
    elif choice == 'playlist':
        playlist_url = input("Ingresa la URL de la playlist: ")
        download_playlist(playlist_url)
    else:
        print("Opción no válida. Elige 'v' para video o 'playlist' para playlist.")









