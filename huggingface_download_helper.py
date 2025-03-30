# an utility to download huggingface models 
import click 
import httpx 
from pathlib import Path 

@click.command() 
@click.argument('url')
@click.argument('output_path', default='/home/srk/Desktop/projects/fastdaimaCodeAssist/models/gguf')
def download_helper(url, output_path):    
    with httpx.stream('GET', url, follow_redirects=True) as response: 
        total_size = response.headers.get('content-length')
        filename = url.split('/')[-1]
        download_path = Path(output_path)/filename
        if download_path.exists(): raise click.ClickException(f'file exists in this dir:{download_path}')

        with open(download_path, 'wb') as fp: 
            if total_size: 
                total_size = int(total_size)
                with click.progressbar(length=total_size, label=f'Downloading {get_data_size(total_size)}') as bar:
                    for data in response.iter_bytes(1024):
                        fp.write(data)
                        bar.update(len(data)) 
            else: 
                for data in response.iter_bytes(1024):
                    fp.write(data)
        click.echo(f'Downloaded data to {download_path}', err=True)

def get_data_size(bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0: break 
        bytes /= 1024.0
    return f'{bytes:.2f} {unit}'

if __name__ == '__main__':
    download_helper() 

