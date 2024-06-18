import Carousel from 'react-bootstrap/Carousel';
import 'bootstrap/dist/css/bootstrap.min.css';

const images = [
  { signed_url: 'https://picsum.photos/200', alt: 'Image 1 Description' },
  { signed_url: 'https://picsum.photos/400?', alt: 'Image 2 Description' },
  { signed_url: 'https://picsum.photos/600/300#f', alt: 'Image 3 Description' },
  { signed_url: 'https://picsum.photos/200/300#f', alt: 'Image 3 Description' },
];


// function ImageCarousel() {
//   const images = [
//     { src: 'https://picsum.photos/200', alt: 'Image 1 Description' },
//     { src: 'https://picsum.photos/200?', alt: 'Image 2 Description' },
//     { src: 'https://picsum.photos/200#f', alt: 'Image 3 Description' },
//     // ... more images
//   ];


//   return (
//     <Carousel>
//       {images.map((image, index) => (
//         <Carousel.Item key={index}> 
//           <img
//             className="d-block w-100" 
//             src={image.src}
//             alt={image.alt}
//           />
//         </Carousel.Item>
//       ))}
//     </Carousel>
//   );
// }

function ImageCarousel({ carouselImages = images}) {
  const maxImagesToDisplay = 4;
  const localApiData = carouselImages.slice(0, maxImagesToDisplay);

  return (localApiData.length > 1) ? (
    <Carousel interval={2000}>
      {localApiData.slice(0, maxImagesToDisplay).map((image, index) => (
        <Carousel.Item key={index}> 
          <img
            className="d-block w-100" 
            src={image.signed_url}
            alt={`Number ${index + 1}`}
          />
        </Carousel.Item>
      ))}
    </Carousel>
  ): (<img className="d-block w-100" src={localApiData[0].signed_url} alt={localApiData[0].alt} />)
}


export default ImageCarousel;